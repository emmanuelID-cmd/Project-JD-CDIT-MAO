"""Policy-independent structural validation of proposed Triage outputs.

A successful structural check never establishes factual grounding, approves
an urgency, or authorizes a downstream handoff.
"""
from __future__ import annotations

from typing import Literal

from pydantic import ValidationError

from cdit_support_mao.agents.triage.input import TriageInput
from cdit_support_mao.contracts.common import StrictModel
from cdit_support_mao.contracts.handoffs import TriageHandoff


class TriageStructureCheck(StrictModel):
    status: Literal["invalid", "structure_valid_needs_grounding"]
    reason_code: Literal["invalid_input", "invalid_output", "context_mismatch", "checkpoint_mismatch", "grounding_not_checked"]
    downstream_allowed: Literal[False] = False
    human_review_required: Literal[True] = True


def validate_triage_structure(packet: object, candidate: object) -> TriageStructureCheck:
    """Validate shape and run binding only; do not evaluate or forward claims."""
    if not isinstance(packet, TriageInput):
        return TriageStructureCheck(status="invalid",reason_code="invalid_input")
    try:
        packet = TriageInput.model_validate(packet.model_dump())
    except ValidationError:
        return TriageStructureCheck(status="invalid",reason_code="invalid_input")
    raw = candidate.model_dump() if isinstance(candidate, TriageHandoff) else candidate
    if isinstance(raw, dict):
        raw_context = raw.get("context")
        if not isinstance(raw_context, dict) or type(raw_context.get("case_version")) is not int:
            return TriageStructureCheck(status="invalid",reason_code="invalid_output")
    try:
        result = TriageHandoff.model_validate(raw)
    except ValidationError:
        return TriageStructureCheck(status="invalid",reason_code="invalid_output")
    if result.context != packet.context or result.contract_version != packet.contract_version:
        return TriageStructureCheck(status="invalid",reason_code="context_mismatch")
    if result.checkpoint.checkpoint != "A2":
        return TriageStructureCheck(status="invalid",reason_code="checkpoint_mismatch")
    return TriageStructureCheck(status="structure_valid_needs_grounding",reason_code="grounding_not_checked")
