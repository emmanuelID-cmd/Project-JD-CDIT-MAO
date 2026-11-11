"""Load and validate the approved, versioned synthetic knowledge set.

Only files marked ``"data_classification": "synthetic"`` load. CDIT-private or
real customer documents must never be placed in the knowledge directory without
an approved data-handling path (AGENTS.md, PRD "Data sources and constraints").
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, model_validator

from cdit_support_mao.contracts.common import ReasonCode, StrictModel

KNOWLEDGE_DIR_ENV = "CDIT_KNOWLEDGE_DIR"
DEFAULT_KNOWLEDGE_DIR = Path("synthetic_data/knowledge")
# src/cdit_support_mao/agents/<agent>/<module>.py -> repository root.
_PROJECT_ROOT = Path(__file__).resolve().parents[4]


class CorpusError(ValueError):
    """The knowledge set is missing or invalid; retrieval must not proceed."""


class KbStep(StrictModel):
    step_id: str = Field(pattern=r"^st[0-9]+$")
    action_type: str = Field(pattern=r"^[a-z][a-z_]*$")
    text: str = Field(min_length=1, max_length=500)


class KbInformationNeeded(StrictModel):
    field: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    prompt: str = Field(min_length=1, max_length=300)


class KbStopCondition(StrictModel):
    condition_id: str = Field(min_length=1, max_length=40)
    text: str = Field(min_length=1, max_length=500)


class KbSection(StrictModel):
    section_id: str = Field(pattern=r"^s[0-9]+$")
    heading: str = Field(min_length=1, max_length=200)
    text: str = Field(min_length=1, max_length=4000)
    steps: tuple[KbStep, ...] = ()
    information_needed: tuple[KbInformationNeeded, ...] = ()
    stop_conditions: tuple[KbStopCondition, ...] = ()

    @model_validator(mode="after")
    def _unique_steps(self) -> KbSection:
        step_ids = [step.step_id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            raise ValueError(f"duplicate step ids in section {self.section_id}")
        return self


class KbArticle(StrictModel):
    doc_id: str = Field(pattern=r"^KB-[A-Z]+-[0-9]{3}$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+$")
    title: str = Field(min_length=1, max_length=200)
    topic: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    product_area: str = Field(pattern=r"^[a-z][a-z0-9_]*$")
    status: Literal["approved", "draft", "retired"]
    data_classification: Literal["synthetic"]
    owner: str = Field(min_length=1, max_length=120)
    effective_date: date
    review_due: date
    keywords: tuple[str, ...] = ()
    sections: tuple[KbSection, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def _consistent(self) -> KbArticle:
        if self.review_due <= self.effective_date:
            raise ValueError(f"{self.doc_id} v{self.version}: review_due must follow effective_date")
        section_ids = [section.section_id for section in self.sections]
        if len(section_ids) != len(set(section_ids)):
            raise ValueError(f"{self.doc_id} v{self.version}: duplicate section ids")
        return self


def ineligibility_reason(article: KbArticle, as_of: date) -> ReasonCode | None:
    """Return why an article may not ground guidance on ``as_of``, or None if it may."""
    if article.status == "draft":
        return ReasonCode.SOURCE_UNAPPROVED
    if article.status == "retired":
        return ReasonCode.SOURCE_RETIRED
    if as_of < article.effective_date:
        return ReasonCode.SOURCE_NOT_EFFECTIVE
    if as_of > article.review_due:
        return ReasonCode.SOURCE_STALE
    return None


@dataclass(frozen=True)
class KnowledgeCorpus:
    articles: tuple[KbArticle, ...]
    source_set_version: str

    def eligible_articles(self, as_of: date) -> tuple[KbArticle, ...]:
        return tuple(a for a in self.articles if ineligibility_reason(a, as_of) is None)

    def approved_versions_by_doc(self, as_of: date) -> dict[str, tuple[KbArticle, ...]]:
        grouped: dict[str, list[KbArticle]] = defaultdict(list)
        for article in self.eligible_articles(as_of):
            grouped[article.doc_id].append(article)
        return {doc_id: tuple(items) for doc_id, items in grouped.items()}


def default_knowledge_dir() -> Path:
    """Configured directory; a relative path missing from the working directory
    resolves against the project root, so the app works from any start folder."""
    path = Path(os.environ.get(KNOWLEDGE_DIR_ENV, str(DEFAULT_KNOWLEDGE_DIR))).expanduser()
    if not path.is_absolute() and not path.exists() and (_PROJECT_ROOT / path).exists():
        return _PROJECT_ROOT / path
    return path


def load_corpus(directory: Path | None = None) -> KnowledgeCorpus:
    """Load every ``*.json`` article in ``directory``; fail closed on any invalid file."""
    directory = directory or default_knowledge_dir()
    if _evaluation_manifest_path(directory) is not None:
        raise CorpusError(
            f"{directory} holds evaluation-only fixtures; load them with load_evaluation_corpus"
        )
    return _corpus_from(_load_articles(directory))


def _load_articles(directory: Path) -> list[KbArticle]:
    if not directory.is_dir():
        raise CorpusError(f"knowledge directory not found: {directory}")
    files = sorted(directory.glob("*.json"))
    if not files:
        raise CorpusError(f"no knowledge articles found in {directory}")

    articles: list[KbArticle] = []
    for path in files:
        try:
            articles.append(KbArticle.model_validate(json.loads(path.read_text(encoding="utf-8"))))
        except (json.JSONDecodeError, ValidationError) as error:
            raise CorpusError(f"invalid knowledge article {path.name}: {error}") from error
    return articles


def _corpus_from(articles: list[KbArticle]) -> KnowledgeCorpus:
    seen: set[tuple[str, str]] = set()
    for article in articles:
        key = (article.doc_id, article.version)
        if key in seen:
            raise CorpusError(f"duplicate article version {article.doc_id} v{article.version}")
        seen.add(key)

    articles = sorted(articles, key=lambda a: (a.doc_id, a.version))
    canonical = json.dumps(
        [a.model_dump(mode="json") for a in articles], sort_keys=True, separators=(",", ":")
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12].upper()
    return KnowledgeCorpus(articles=tuple(articles), source_set_version=f"SRC-{digest}")


# --- Evaluation-only fixture sets -------------------------------------------------
#
# A fixture set holds synthetic articles written only so an evaluation dataset can be
# source-grounded. It is never part of the default runtime corpus: the runtime loads
# ``synthetic_data/knowledge`` alone, and ``load_corpus`` refuses a fixture-set folder.
# An evaluation loads the base corpus plus one fixture set with ``load_evaluation_corpus``.
# The articles keep the normal schema (``status: approved`` is what makes them
# retrievable in that evaluation); the manifest records that the approval is test-only.

EVALUATION_MANIFEST = "manifest.json"
EVALUATION_ARTICLES_DIR = "articles"


class EvaluationFixtureManifest(StrictModel):
    fixture_set_id: str = Field(pattern=r"^SYN-[A-Z0-9][A-Z0-9-]*$")
    version: str = Field(pattern=r"^[0-9]+\.[0-9]+$")
    use: Literal["evaluation_only"]
    data_classification: Literal["synthetic"]
    evaluation_dataset_id: str = Field(min_length=1, max_length=120)
    evaluation_as_of: date
    notice: str = Field(min_length=1, max_length=1000)
    provenance: str = Field(min_length=1, max_length=1000)


@dataclass(frozen=True)
class EvaluationCorpus:
    corpus: KnowledgeCorpus
    manifest: EvaluationFixtureManifest
    fixture_doc_ids: frozenset[str]


def _evaluation_manifest_path(directory: Path) -> Path | None:
    """The manifest that marks ``directory`` (or its parent) as an evaluation fixture set."""
    for candidate in (directory / EVALUATION_MANIFEST, directory.parent / EVALUATION_MANIFEST):
        if candidate.is_file():
            return candidate
    return None


def load_evaluation_manifest(fixture_set_dir: Path) -> EvaluationFixtureManifest:
    path = fixture_set_dir / EVALUATION_MANIFEST
    try:
        return EvaluationFixtureManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except FileNotFoundError as error:
        raise CorpusError(f"evaluation fixture manifest not found: {path}") from error
    except (json.JSONDecodeError, ValidationError) as error:
        raise CorpusError(f"invalid evaluation fixture manifest {path}: {error}") from error


def load_evaluation_corpus(fixture_set_dir: Path, base_dir: Path | None = None) -> EvaluationCorpus:
    """Base corpus plus one evaluation-only fixture set; fail closed on any conflict.

    A fixture may not reuse a base ``doc_id``: that would add a second version of a
    runtime article and change how the base article is retrieved.
    """
    manifest = load_evaluation_manifest(fixture_set_dir)
    base_dir = base_dir or default_knowledge_dir()
    if _evaluation_manifest_path(base_dir) is not None:
        raise CorpusError(f"base corpus {base_dir} must not be an evaluation fixture set")
    base = _load_articles(base_dir)
    fixtures = _load_articles(fixture_set_dir / EVALUATION_ARTICLES_DIR)
    base_ids = {article.doc_id for article in base}
    clashes = sorted({article.doc_id for article in fixtures} & base_ids)
    if clashes:
        raise CorpusError(f"evaluation fixtures reuse base doc_ids: {', '.join(clashes)}")
    return EvaluationCorpus(
        corpus=_corpus_from(base + fixtures),
        manifest=manifest,
        fixture_doc_ids=frozenset(article.doc_id for article in fixtures),
    )
