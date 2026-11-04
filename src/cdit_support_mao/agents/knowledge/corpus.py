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
    return Path(os.environ.get(KNOWLEDGE_DIR_ENV, str(DEFAULT_KNOWLEDGE_DIR))).expanduser()


def load_corpus(directory: Path | None = None) -> KnowledgeCorpus:
    """Load every ``*.json`` article in ``directory``; fail closed on any invalid file."""
    directory = directory or default_knowledge_dir()
    if not directory.is_dir():
        raise CorpusError(f"knowledge directory not found: {directory}")
    files = sorted(directory.glob("*.json"))
    if not files:
        raise CorpusError(f"no knowledge articles found in {directory}")

    articles: list[KbArticle] = []
    seen: set[tuple[str, str]] = set()
    for path in files:
        try:
            article = KbArticle.model_validate(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValidationError) as error:
            raise CorpusError(f"invalid knowledge article {path.name}: {error}") from error
        key = (article.doc_id, article.version)
        if key in seen:
            raise CorpusError(f"duplicate article version {article.doc_id} v{article.version}")
        seen.add(key)
        articles.append(article)

    articles.sort(key=lambda a: (a.doc_id, a.version))
    canonical = json.dumps(
        [a.model_dump(mode="json") for a in articles], sort_keys=True, separators=(",", ":")
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:12].upper()
    return KnowledgeCorpus(articles=tuple(articles), source_set_version=f"SRC-{digest}")
