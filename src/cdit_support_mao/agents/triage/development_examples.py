"""Versioned, synthetic-only development example references for Triage.

Rows are copied mechanically from trusted-provisioned CASE-SCENARIOS.md bytes.
They are development examples, not approved evaluation labels or policy.
This fixture lookup does not independently verify the origin of supplied bytes.
"""
from __future__ import annotations

import hashlib
import re
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Literal

from pydantic import Field, field_validator, model_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef, StrictModel


class DevelopmentCatalogError(ValueError):
    """Content-free development-catalog failure."""


TRUSTED_CATEGORY_SCENARIOS_SHA256 = "010077c54532b166b6116656691c579915897a88d56ab0d56cf7b6cd8f62be60"


class DevelopmentExample(StrictModel):
    row: int = Field(strict=True, ge=1, le=80)
    category: str = Field(min_length=1, max_length=100)
    sample_query: str = Field(min_length=1, max_length=1000, repr=False)
    sample_band: Literal["Low [P3]", "Medium [P2]", "High [P1]"]
    conditions: str = Field(min_length=1, max_length=1000, repr=False)

    @field_validator("category")
    @classmethod
    def category_is_bounded_text(cls, value: str) -> str:
        if not value.strip() or any(ord(char) < 32 for char in value):
            raise ValueError("invalid_category")
        return value


class DevelopmentReference(StrictModel):
    claimed_source_path: Literal["docs/requirements/CASE-SCENARIOS.md"] = "docs/requirements/CASE-SCENARIOS.md"
    source_origin: Literal["unverified_provisioner_claim"] = "unverified_provisioner_claim"
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    row: int = Field(strict=True, ge=1, le=80)
    example_id: str = Field(pattern=r"^SYN-EXAMPLE-[0-9]{3}$")
    example_category: str
    example_band: Literal["Low [P3]", "Medium [P2]", "High [P1]"]
    content_trust: Literal["untrusted_synthetic_example"] = "untrusted_synthetic_example"
    sample_status: Literal["unverified_synthetic_development_example"] = "unverified_synthetic_development_example"

    @model_validator(mode="after")
    def id_matches_row(self) -> DevelopmentReference:
        if self.example_id != f"SYN-EXAMPLE-{self.row:03d}":
            raise ValueError("example_id_row_mismatch")
        return self


class DevelopmentCategoryTaxonomy(StrictModel):
    """Approved synthetic category vocabulary, separate from example labels.

    Only category names are exposed to semantic Triage. Example queries,
    urgency bands, and condition text remain development examples and are not
    treated as gold labels or operating policy.
    """

    categories: tuple[str, ...] = Field(min_length=1, max_length=80)
    source: SourceRef
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    taxonomy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    scope: Literal["synthetic_category_vocabulary_only"] = "synthetic_category_vocabulary_only"
    operational_policy: Literal[False] = False
    example_rows_are_labels: Literal[False] = False

    @model_validator(mode="after")
    def taxonomy_is_version_bound(self) -> DevelopmentCategoryTaxonomy:
        if len(self.categories) != len(set(self.categories)) or any(not name.strip() for name in self.categories):
            raise ValueError("invalid_category_taxonomy")
        expected_taxonomy_digest = hashlib.sha256(
            "\n".join(self.categories).encode("utf-8")
        ).hexdigest()
        expected_version = f"sha256-{expected_taxonomy_digest[:16]}"
        if (self.source.kind is not SourceKind.POLICY_RULE
                or self.source.source_id != "SYN-TICKET-CATEGORY-TAXONOMY"
                or self.source.version != expected_version
                or self.source.locator != "category_names"
                or self.taxonomy_sha256 != expected_taxonomy_digest):
            raise ValueError("category_taxonomy_source_mismatch")
        return self


def load_project_category_taxonomy() -> DevelopmentCategoryTaxonomy:
    """Load the pinned project taxonomy source; fail closed if it changed.

    The complete case-scenario document is never sent to the model. This loader
    extracts the category names only and pins the exact synthetic source bytes
    so an arbitrary caller-supplied taxonomy cannot expand the model vocabulary.
    Updating the source requires an intentional pin update and review.
    """
    source_path = Path(__file__).resolve().parents[4] / "docs" / "requirements" / "CASE-SCENARIOS.md"
    try:
        source_bytes = source_path.read_bytes()
    except OSError:
        raise DevelopmentCatalogError("trusted_category_taxonomy_unavailable") from None
    if hashlib.sha256(source_bytes).hexdigest() != TRUSTED_CATEGORY_SCENARIOS_SHA256:
        raise DevelopmentCatalogError("trusted_category_taxonomy_changed")
    capability = object()
    catalog = DevelopmentExampleCatalog(provisioning_capability=capability)
    catalog.provision(source_bytes, capability=capability)
    return catalog.category_taxonomy()


class DevelopmentLookup(StrictModel):
    context: RunContext
    handoff_id: str
    handoff_state_version: int = Field(strict=True, ge=2)
    item_index: int = Field(strict=True, ge=1, le=8)
    status: Literal["exact_reference_only", "no_reference", "ambiguous_segmentation"]
    references: tuple[DevelopmentReference, ...] = ()
    uncertainty: tuple[str, ...] = (
        "Reporter statements are unverified; exact text equality does not establish facts or full context.",
        "Impact, timing, exceptions, and differences from the parent case have not been assessed.",
        "The example is not approved policy, a human-approved evaluation label, or proof of CDIT support scope.",
    )
    category: Literal["unknown"] = "unknown"
    urgency: Literal["unknown"] = "unknown"
    destination: Literal["unknown"] = "unknown"
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False


class DevelopmentExampleCatalog:
    """Immutable after trusted fixture provisioning; no reviewer authentication.

    A private capability prevents accidental in-process provisioning, not
    hostile same-process code. The SHA-256 identifies supplied bytes; trusted
    fixture setup must establish that they are the intended project file.
    """
    def __init__(self, *, provisioning_capability: object):
        if provisioning_capability is None or isinstance(provisioning_capability, (str, bytes, int, float, bool)):
            raise DevelopmentCatalogError("invalid_fixture_capability")
        self._capability = provisioning_capability
        self._entries: tuple[DevelopmentExample, ...] | None = None
        self._digest: str | None = None
        self._lock = Lock()

    def provision(self, source_bytes: bytes, *, capability: object) -> None:
        if capability is not self._capability:
            raise DevelopmentCatalogError("unauthorized_fixture_provision")
        if not isinstance(source_bytes, bytes) or len(source_bytes) > 2_000_000:
            raise DevelopmentCatalogError("invalid_source")
        try:
            text = source_bytes.decode("utf-8-sig")
            start = text.index("## Generic ticket-condition catalog and proposed urgency")
            end = text.index("### Triage overrides and handling boundaries", start)
            section = text[start:end]
            rows = []
            for line in section.splitlines():
                if not re.match(r"^\|\s*\d+\s*\|", line):
                    continue
                columns = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(columns) != 5:
                    raise ValueError("invalid_columns")
                number, category, query, band, conditions = columns
                if len(query) < 2 or query[0] != "“" or query[-1] != "”":
                    raise ValueError("invalid_quote")
                rows.append(DevelopmentExample(row=int(number), category=category,
                    sample_query=query[1:-1], sample_band=band, conditions=conditions))
            if sorted(row.row for row in rows) != list(range(1, 81)):
                raise ValueError("invalid_row_set")
        except (UnicodeDecodeError, ValueError, TypeError):
            raise DevelopmentCatalogError("invalid_source_table") from None
        digest = hashlib.sha256(source_bytes).hexdigest()
        with self._lock:
            if self._entries is not None:
                raise DevelopmentCatalogError("catalog_already_provisioned")
            self._entries, self._digest = tuple(rows), digest

    def _snapshot(self) -> tuple[tuple[DevelopmentExample, ...], str]:
        with self._lock:
            if self._entries is None or self._digest is None:
                raise DevelopmentCatalogError("catalog_not_provisioned")
            return self._entries, self._digest

    def category_taxonomy(self) -> DevelopmentCategoryTaxonomy:
        """Return only the approved category names with source/version binding.

        Example queries, bands, and conditions are deliberately excluded.
        """
        entries, digest = self._snapshot()
        categories = tuple(dict.fromkeys(row.category for row in entries))
        taxonomy_digest = hashlib.sha256("\n".join(categories).encode("utf-8")).hexdigest()
        return DevelopmentCategoryTaxonomy(
            categories=categories,
            source=SourceRef(
                kind=SourceKind.POLICY_RULE,
                source_id="SYN-TICKET-CATEGORY-TAXONOMY",
                version=f"sha256-{taxonomy_digest[:16]}",
                locator="category_names",
            ),
            source_sha256=digest,
            taxonomy_sha256=taxonomy_digest,
        )


def lookup_development_examples(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext, item_index: int,
    catalog: DevelopmentExampleCatalog, now: datetime | None = None,
) -> DevelopmentLookup:
    """Reference exact example text without classifying the current case.

    Case-sensitive whole-item equality does not establish context or truth.
    A match references examples only; a non-match is not a no-risk result.
    Consumer access, ownership and freshness need rechecking at actual use.
    """
    if not isinstance(catalog, DevelopmentExampleCatalog):
        raise HandoffError("invalid_development_catalog")
    rows, digest = catalog._snapshot()
    parts = extract_request_parts(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    if type(item_index) is not int or not 1 <= item_index <= len(parts.items):
        raise HandoffError("invalid_request_item")
    item = parts.items[item_index - 1]
    references = ()
    if parts.status == "needs_auditor":
        status = "ambiguous_segmentation"
    else:
        references = tuple(DevelopmentReference(source_sha256=digest, row=row.row,
            example_id=f"SYN-EXAMPLE-{row.row:03d}",
            example_category=row.category, example_band=row.sample_band)
            for row in rows if row.sample_query == item.reported_text)
        status = "exact_reference_only" if references else "no_reference"
    result = DevelopmentLookup(context=context, handoff_id=handoff_id,
        handoff_state_version=expected_version, item_index=item_index, status=status, references=references)
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return result
