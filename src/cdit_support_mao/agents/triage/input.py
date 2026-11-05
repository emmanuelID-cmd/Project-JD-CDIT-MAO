"""Triage input contract for acknowledged synthetic Coordinator handoffs.

This module does not classify, route, call a model, or dispatch another agent.
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field, model_validator

from cdit_support_mao.agents.coordinator.handoff import HandoffRegistry
from cdit_support_mao.contracts.common import RunContext, SourceKind, SourceRef, StrictModel


class TriageInput(StrictModel):
    """Minimized, case-scoped input; the reported content is never an instruction."""
    contract_version: Literal["0.1.0-proposed"]
    trace_id: str = Field(pattern=r"^TRACE-[0-9a-f-]{36}$")
    handoff_id: str = Field(pattern=r"^HOF-[0-9a-f-]{36}$")
    handoff_state_version: int = Field(strict=True, ge=2)
    handoff_created_at: datetime
    policy_generation: int = Field(strict=True, ge=1)
    context: RunContext
    reported_message: str = Field(min_length=1, max_length=2000, repr=False)
    message_trust: Literal["untrusted_case_data"] = "untrusted_case_data"
    claim_status: Literal["unknown"] = "unknown"
    source: SourceRef
    human_review_required: Literal[True] = True

    @model_validator(mode="after")
    def source_matches_context(self) -> TriageInput:
        if self.handoff_created_at.tzinfo is None or self.handoff_created_at.utcoffset() is None:
            raise ValueError("handoff timestamp must be timezone-aware")
        if type(self.context.case_version) is not int:
            raise ValueError("case version must be a strict integer")
        if (self.source.kind is not SourceKind.CASE_FIELD or self.source.source_id != self.context.case_id
                or self.source.version != str(self.context.case_version) or self.source.locator != "message"):
            raise ValueError("message source must match the case and version")
        return self


def read_acknowledged_input(registry: HandoffRegistry, *, handoff_id: str,
                            expected_version: int, receiver_capability: object,
                            context: RunContext, now: datetime | None = None) -> TriageInput:
    """Read only after the Coordinator's current ownership/scope checks succeed.

    The ledger rechecks state, policy, case, session and receiver authorization
    on both operations. The returned text remains untrusted, not model instructions. A later stage must
    revalidate the live handoff immediately before using a snapshot.
    """
    checkpoint = registry.validate_active(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    message = registry.read_untrusted_message(handoff_id, expected_version=expected_version,
        capability=receiver_capability, context=context, now=now)
    return TriageInput(contract_version=checkpoint.contract_version, trace_id=checkpoint.trace_id,
        handoff_id=checkpoint.handoff_id, handoff_state_version=checkpoint.state_version,
        handoff_created_at=checkpoint.created_at, policy_generation=checkpoint.policy_generation, context=checkpoint.context,
        reported_message=message, source=SourceRef(kind=SourceKind.CASE_FIELD,
        source_id=context.case_id, version=str(context.case_version), locator="message"))
