"""Provisional lookup over explicitly reviewed *synthetic fixture* examples.

No live identity, storage, semantic model, production authorization, or action
is provided here. Private in-process objects prevent accidental fixture misuse;
they do not authenticate users. Fixture review/provenance assertions are test
metadata, not proof that a person reviewed an item or that data are sanitized.
Only synthetic, already sanitized opaque fact codes may be supplied by trusted
fixture code. All candidates remain inference and require human review.
"""
from __future__ import annotations

from threading import Lock
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from cdit_support_mao.contracts.common import StrictModel


class FixtureCatalogError(ValueError):
    """Fixed, content-free errors; never interpolate supplied fixture data."""


class FactCode(StrictModel):
    """A bounded synthetic fixture code, not evidence a real fact is true."""
    field: str = Field(pattern=r"^[A-Z][A-Z0-9_]{0,39}$", repr=False)
    value: str = Field(pattern=r"^[A-Z][A-Z0-9_]{0,39}$", repr=False)


class FixtureExampleSource(StrictModel):
    """Opaque reference to a synthetic example; not an approved policy rule."""
    source_id: str = Field(pattern=r"^SYN-EXAMPLE-[A-Z0-9-]{1,40}$")
    version: str = Field(pattern=r"^[A-Z0-9][A-Z0-9._-]{0,29}$")


class FixtureExample(StrictModel):
    source: FixtureExampleSource
    reviewed_fixture: Literal[True]
    review_fixture_ref: str = Field(pattern=r"^SYN-REVIEW-[A-Z0-9-]{1,40}$")
    conditions: tuple[FactCode, ...] = Field(min_length=1, max_length=32, repr=False)
    exceptions: tuple[FactCode, ...] = Field(default=(), max_length=32, repr=False)

    @field_validator("reviewed_fixture", mode="before")
    @classmethod
    def _strict_fixture_marker(cls, value: object) -> bool:
        if value is not True:
            raise ValueError("fixture_review_marker_required")
        return True

    @model_validator(mode="after")
    def _unique_fields(self) -> FixtureExample:
        fields = [item.field for item in self.conditions]
        exceptions = [item.field for item in self.exceptions]
        if len(fields) != len(set(fields)) or len(exceptions) != len(set(exceptions)):
            raise ValueError("duplicate_fact_field")
        return self


class FactComparison(StrictModel):
    """A comparison, not a verified assertion. Fields are hidden from repr."""
    expected: FactCode = Field(repr=False)
    observed: FactCode | None = Field(default=None, repr=False)
    relation: Literal["matched", "missing", "different"]


class ExampleCandidate(StrictModel):
    source: FixtureExampleSource
    review_fixture_ref: str = Field(pattern=r"^SYN-REVIEW-[A-Z0-9-]{1,40}$")
    label: Literal["inference"] = "inference"
    conditions: tuple[FactComparison, ...] = Field(repr=False)
    exceptions: tuple[FactComparison, ...] = Field(repr=False)
    unassessed_observed: tuple[FactCode, ...] = Field(default=(), repr=False)
    human_review_required: Literal[True] = True
    category: None = None
    urgency: None = None
    destination: None = None
    dispatch_allowed: Literal[False] = False


class LookupResult(StrictModel):
    status: Literal["candidates_found", "no_shared_conditions", "version_mismatch"]
    catalog_version: str
    candidates: tuple[ExampleCandidate, ...] = ()
    observed_facts: tuple[FactCode, ...] = Field(default=(), repr=False)
    human_review_required: Literal[True] = True
    dispatch_allowed: Literal[False] = False


def _valid_capability(capability: object) -> bool:
    return capability is not None and not isinstance(capability, (str, bytes, int, float, bool))


def _compare(expected: FactCode, observed: dict[str, FactCode]) -> FactComparison:
    item = observed.get(expected.field)
    relation = "missing" if item is None else ("matched" if item.value == expected.value else "different")
    return FactComparison(expected=expected, observed=item, relation=relation)


class SyntheticFixtureExampleCatalog:
    """Bounded process-local fixture catalog; not a durable or secure store.

    Trusted fixture code owns both capabilities and supplies only sanitized
    synthetic fact codes. No reviewer identity or real approval is verified.
    A changed catalog needs a distinct version; duplicate IDs are rejected.
    Sealing freezes this instance only: other instances can reuse its version
    for different contents. Integration requires a trusted digest/version registry.
    """
    def __init__(self, *, catalog_version: str, provisioning_capability: object, lookup_capability: object):
        if not _valid_capability(provisioning_capability) or not _valid_capability(lookup_capability) or provisioning_capability is lookup_capability:
            raise FixtureCatalogError("invalid_fixture_capabilities")
        try:
            # Reuse the bounded version field, without interpreting it as approval.
            version = FixtureExampleSource(source_id="SYN-EXAMPLE-CATALOG", version=catalog_version).version
        except ValidationError:
            raise FixtureCatalogError("invalid_catalog_version") from None
        self._catalog_version = version
        self._provisioning_capability = provisioning_capability
        self._lookup_capability = lookup_capability
        self._examples: dict[str, FixtureExample] = {}
        self._lock = Lock()
        self._sealed = False

    def provision(self, fixture: object, *, capability: object) -> None:
        if capability is not self._provisioning_capability:
            raise FixtureCatalogError("unauthorized_fixture_provision")
        try:
            raw = fixture.model_dump() if isinstance(fixture, FixtureExample) else fixture
            example = FixtureExample.model_validate(raw)
        except (ValidationError, TypeError, ValueError):
            raise FixtureCatalogError("invalid_reviewed_fixture") from None
        with self._lock:
            if self._sealed:
                raise FixtureCatalogError("catalog_sealed")
            if example.source.source_id in self._examples:
                raise FixtureCatalogError("duplicate_example_id")
            if len(self._examples) >= 100:
                raise FixtureCatalogError("fixture_catalog_full")
            self._examples[example.source.source_id] = example

    def seal(self, *, capability: object) -> None:
        """Freeze fixture contents before lookup; replacements need a new catalog."""
        if capability is not self._provisioning_capability:
            raise FixtureCatalogError("unauthorized_fixture_provision")
        with self._lock:
            self._sealed = True

    def lookup(self, observed_facts: object, *, expected_catalog_version: str, capability: object) -> LookupResult:
        if capability is not self._lookup_capability:
            raise FixtureCatalogError("unauthorized_fixture_lookup")
        with self._lock:
            if not self._sealed:
                raise FixtureCatalogError("catalog_not_sealed")
            if expected_catalog_version != self._catalog_version:
                return LookupResult(status="version_mismatch", catalog_version=self._catalog_version)
            examples = tuple(self._examples.values())
        if not isinstance(observed_facts, (tuple, list)) or len(observed_facts) > 32:
            raise FixtureCatalogError("invalid_observed_facts")
        try:
            facts = tuple(FactCode.model_validate(f.model_dump() if isinstance(f, FactCode) else f) for f in observed_facts)
        except (ValidationError, TypeError, ValueError):
            raise FixtureCatalogError("invalid_observed_facts") from None
        if len({fact.field for fact in facts}) != len(facts):
            raise FixtureCatalogError("duplicate_observed_field")
        observed = {fact.field: fact for fact in facts}
        candidates = []
        for example in examples:
            conditions = tuple(_compare(fact, observed) for fact in example.conditions)
            if not any(item.relation == "matched" for item in conditions):
                continue
            exceptions = tuple(_compare(fact, observed) for fact in example.exceptions)
            assessed_fields = {fact.field for fact in (*example.conditions, *example.exceptions)}
            unassessed = tuple(fact for fact in facts if fact.field not in assessed_fields)
            candidates.append(ExampleCandidate(source=example.source, review_fixture_ref=example.review_fixture_ref, conditions=conditions, exceptions=exceptions,
                unassessed_observed=unassessed))
        candidates.sort(key=lambda item: (-sum(c.relation == "matched" for c in item.conditions), item.source.source_id))
        return LookupResult(status="candidates_found" if candidates else "no_shared_conditions",
            catalog_version=self._catalog_version, candidates=tuple(candidates), observed_facts=facts)
