"""Exact synthetic fixture rules for provisional Triage proposals only.

The capability is process-local fixture plumbing, not real authentication or
proof of policy approval. Rules are explicitly provisioned; the 80 example
catalog is never used as policy. No model, ticket update, route or dispatch.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from threading import Lock
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffError, HandoffRegistry
from cdit_support_mao.agents.triage.segment import extract_request_parts
from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef, StrictModel


class FixturePolicyError(ValueError):
    """Content-free fixture provisioning error."""


class SyntheticRule(StrictModel):
    rule_id: str = Field(pattern=r"^SYN-RULE-[A-Z0-9][A-Z0-9-]{0,39}$")
    exact_report: str = Field(min_length=1, max_length=1000, repr=False)
    category: str = Field(pattern=r"^[a-z][a-z0-9-]{0,39}$")
    urgency: Literal["low", "medium", "high"]
    proposed_destination: Literal["knowledge_review"]

    @field_validator("exact_report")
    @classmethod
    def report_is_single_line(cls, value: str) -> str:
        if not value.strip() or value != value.strip() or any(ord(c) < 32 for c in value):
            raise ValueError("invalid_fixture_report")
        return value


class SyntheticPolicyCatalog:
    """Sealed local fixture rules, not a trusted policy registry or approval.

    A separate instance may assert the same version with different contents.
    The digest identifies this fixture's contents, not authorization, review or
    verified source origin. Use only with trusted, synthetic fixture code.
    """
    def __init__(self, *, policy_version: str, provision_capability: object):
        if (not isinstance(policy_version, str) or not policy_version.startswith("SYN-")
                or len(policy_version) > 60 or not policy_version.isascii()
                or not all(c.isalnum() or c in "-." for c in policy_version)):
            raise FixturePolicyError("invalid_fixture_policy_version")
        if provision_capability is None or isinstance(provision_capability, (str, bytes, int, float, bool)):
            raise FixturePolicyError("invalid_fixture_capability")
        self._version = policy_version
        self._capability = provision_capability
        self._rules: dict[str, SyntheticRule] = {}
        self._sealed = False
        self._lock = Lock()

    def add(self, value: object, *, capability: object) -> None:
        if capability is not self._capability:
            raise FixturePolicyError("unauthorized_fixture_provision")
        try:
            raw = value.model_dump() if isinstance(value, SyntheticRule) else value
            rule = SyntheticRule.model_validate(raw)
        except (ValidationError, ValueError, TypeError):
            raise FixturePolicyError("invalid_fixture_rule") from None
        with self._lock:
            if self._sealed or rule.rule_id in self._rules or len(self._rules) >= 100:
                raise FixturePolicyError("fixture_catalog_not_mutable")
            self._rules[rule.rule_id] = rule

    def seal(self, *, capability: object) -> None:
        if capability is not self._capability:
            raise FixturePolicyError("unauthorized_fixture_provision")
        with self._lock:
            self._sealed = True

    def _snapshot(self) -> tuple[str, str, tuple[SyntheticRule, ...]]:
        with self._lock:
            if not self._sealed:
                raise FixturePolicyError("fixture_catalog_not_sealed")
            rules = tuple(sorted(self._rules.values(), key=lambda r: r.rule_id))
        raw = json.dumps({"version": self._version, "rules": [r.model_dump() for r in rules]},
                         sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        return self._version, hashlib.sha256(raw).hexdigest(), rules


class FixturePolicyProposal(StrictModel):
    trace_id: str
    handoff_id: str
    handoff_state_version: int = Field(strict=True, ge=2)
    context: RunContext
    item_index: int = Field(strict=True, ge=1, le=8)
    item_count: int = Field(strict=True, ge=1, le=8)
    reported_source: SourceRef
    start_codepoint: int = Field(strict=True, ge=0)
    end_codepoint: int = Field(strict=True, ge=1)
    source_check: Literal["exact_case_message_span_only"] = "exact_case_message_span_only"
    status: Literal["synthetic_fixture_inference", "abstained_needs_human"]
    reason: Literal["exact_fixture_rule", "ambiguous_parent", "policy_unavailable", "policy_version_mismatch", "no_matching_rule", "conflicting_rules"]
    proposed_category: str | None = None
    proposed_urgency: Literal["low", "medium", "high"] | None = None
    proposed_destination: Literal["knowledge_review"] | None = None
    claim_label: Literal["inference", "unknown"]
    policy_source: SourceRef | None = None
    fixture_digest: str | None = Field(default=None, pattern=r"^[0-9a-f]{64}$")
    policy_origin: Literal["synthetic_fixture_not_verified_or_approved"] = "synthetic_fixture_not_verified_or_approved"
    source_report_is_verified_event: Literal[False] = False
    confidence: Literal["low"] = "low"
    confidence_calibrated: Literal[False] = False
    semantic_completeness: Literal["unknown"] = "unknown"
    full_parent_context_reviewed: Literal[False] = False
    human_review_required: Literal[True] = True
    downstream_allowed: Literal[False] = False
    dispatched: Literal[False] = False
    parent_complete: Literal[False] = False

    @model_validator(mode="after")
    def consistency(self) -> FixturePolicyProposal:
        if (self.reported_source.kind is not SourceKind.CASE_FIELD
                or self.reported_source.source_id != self.context.case_id
                or self.reported_source.version != str(self.context.case_version)
                or self.reported_source.locator != "message"
                or self.start_codepoint >= self.end_codepoint):
            raise ValueError("invalid_case_source")
        values = (self.proposed_category, self.proposed_urgency, self.proposed_destination,
                  self.policy_source, self.fixture_digest)
        if self.status == "synthetic_fixture_inference":
            if (self.reason != "exact_fixture_rule" or self.claim_label != "inference"
                    or any(v is None for v in values) or self.item_count != 1
                    or self.policy_source.kind is not SourceKind.POLICY_RULE
                    or self.policy_source.version != self.context.policy_version
                    or not self.policy_source.source_id.startswith("SYN-RULE-")):
                raise ValueError("invalid_fixture_inference")
        elif self.reason == "exact_fixture_rule" or self.claim_label != "unknown" or any(v is not None for v in values):
            raise ValueError("invalid_fixture_abstention")
        if self.item_index > self.item_count:
            raise ValueError("invalid_item_index")
        return self


def propose_from_synthetic_policy(
    registry: HandoffRegistry, *, handoff_id: str, expected_version: int,
    receiver_capability: object, context: RunContext, item_index: int,
    catalog: SyntheticPolicyCatalog | None, now: datetime | None = None,
) -> FixturePolicyProposal:
    """Return one source-bound fixture inference, or an unknown human fallback.

    Only a current Coordinator-acknowledged synthetic handoff is read. Policy
    matching is exact and case-sensitive, requiring one detected parent item.
    This cannot prove semantic completeness, real facts, policy approval, or
    applicability to any actual case. A later consumer must revalidate state,
    identity and scope; the supplied clock is a trusted fixture hook only.
    """
    parts = extract_request_parts(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability,
        context=context, now=now)
    if type(item_index) is not int or not 1 <= item_index <= len(parts.items):
        raise HandoffError("invalid_request_item")
    item = parts.items[item_index - 1]
    reason = "ambiguous_parent" if parts.status == "needs_auditor" or len(parts.items) != 1 else "policy_unavailable"
    version = digest = None
    matches: list[SyntheticRule] = []
    if reason != "ambiguous_parent" and catalog is not None:
        if not isinstance(catalog, SyntheticPolicyCatalog):
            raise HandoffError("invalid_fixture_policy")
        try:
            version, digest, rules = catalog._snapshot()
        except FixturePolicyError as error:
            if str(error) != "fixture_catalog_not_sealed":
                raise
            reason = "policy_unavailable"
        else:
            if version != context.policy_version:
                reason = "policy_version_mismatch"
            else:
                matches = [rule for rule in rules if rule.exact_report == item.reported_text]
                reason = "exact_fixture_rule" if len(matches) == 1 else ("conflicting_rules" if matches else "no_matching_rule")
    selected = matches[0] if reason == "exact_fixture_rule" else None
    result = FixturePolicyProposal(trace_id=parts.trace_id, handoff_id=parts.handoff_id,
        handoff_state_version=expected_version, context=parts.context,
        item_index=item.item_index, item_count=len(parts.items), reported_source=item.source,
        start_codepoint=item.start_codepoint, end_codepoint=item.end_codepoint,
        status="synthetic_fixture_inference" if selected else "abstained_needs_human", reason=reason,
        proposed_category=selected.category if selected else None,
        proposed_urgency=selected.urgency if selected else None,
        proposed_destination=selected.proposed_destination if selected else None,
        claim_label="inference" if selected else "unknown",
        policy_source=SourceRef(kind=SourceKind.POLICY_RULE, source_id=selected.rule_id, version=version) if selected else None,
        fixture_digest=digest if selected else None)
    registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return result
