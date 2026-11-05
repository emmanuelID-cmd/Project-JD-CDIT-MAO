"""Run local synthetic intake fixture checks; no model, database or network."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Literal

from pydantic import Field

from cdit_support_mao.agents.coordinator import Coordinator, FixtureCaseVersions, FixturePolicyVersions, FixtureSession, FixtureSessionAuthority
from cdit_support_mao.contracts.common import StrictModel


class HarnessCase(StrictModel):
    case_id: str = Field(pattern=r"^SYN-[A-Z0-9][A-Z0-9-]{0,58}$")
    message: str = Field(min_length=1, max_length=2000)
    role: Literal["user", "staff", "admin"]
    active: bool = Field(strict=True)
    scoped: bool = Field(strict=True)
    case_version: int = Field(strict=True, ge=1)
    current_version: int = Field(strict=True, ge=1)
    policy_version: str
    expected_status: Literal["ready_for_triage", "rejected_input", "blocked_checkpoint"]
    expected_reason: str | None = None


class FixtureSet(StrictModel):
    version: Literal["manny-a0-a1-dev-v1"]
    cases: tuple[HarnessCase, ...] = Field(min_length=1, max_length=100)


def run_fixture_set(fixtures: FixtureSet) -> list[dict[str, object]]:
    """Compare fixture outcomes without emitting ticket text or session tokens."""
    results = []
    for case in fixtures.cases:
        provisioner = object()
        authority = FixtureSessionAuthority(provisioning_capability=provisioner, ttl_seconds=60)
        versions = FixtureCaseVersions(provisioning_capability=provisioner)
        versions.set_version(case.case_id, case.current_version, expected_version=None, capability=provisioner)
        scope = (case.case_id,) if case.scoped else ("SYN-OTHER",)
        session = FixtureSession(actor_id="SYN-ACTOR-HARNESS", role=case.role, active=case.active, allowed_case_ids=scope)
        token = authority.issue(session, capability=provisioner)
        policies = FixturePolicyVersions(provisioning_capability=provisioner, active=frozenset({"SYN-POLICY-1"}))
        coordinator = Coordinator(authority, case_versions=versions, policy_versions=policies)
        request = {"case_id":case.case_id, "case_version":case.case_version, "policy_version":case.policy_version, "message":case.message, "data_classification":"synthetic"}
        result = coordinator.prepare(request, session_token=token)
        results.append({"case_id":case.case_id, "expected_status":case.expected_status, "actual_status":result.status.value,
                        "expected_reason":case.expected_reason, "actual_reason":result.reason_code,
                        "passed":result.status.value == case.expected_status and result.reason_code == case.expected_reason,
                        "trace_id":result.trace_id, "checkpoint":result.checkpoint})
    return results


def main() -> int:
    parser=argparse.ArgumentParser(description="Run local synthetic Coordinator intake fixture checks")
    parser.add_argument("fixture_file", type=Path)
    args=parser.parse_args()
    if args.fixture_file.stat().st_size > 524288:
        parser.error("fixture file exceeds 512 KiB")
    fixtures=FixtureSet.model_validate_json(args.fixture_file.read_text(encoding="utf-8"))
    results=run_fixture_set(fixtures)
    print(json.dumps({"fixture_version":fixtures.version, "passed":sum(item["passed"] for item in results),
                      "total":len(results), "results":results}, ensure_ascii=False, indent=2))
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
