"""Explicitly authorized synthetic live Triage evaluation for the draft cases.

Each selected case is sent once, sequentially, through the Coordinator A0/A1
and Manny Triage A2 harness. The provider call is billable and requires the
explicit CLI authorization flag. No retries, ticket writes, or dispatch occur.
This run scores Triage only; it is not a full six-agent evaluation.
"""
from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence
from uuid import uuid4

from cdit_support_mao.agents.coordinator import (
    Coordinator,
    FixtureCaseVersions,
    FixturePolicyVersions,
    FixtureSession,
    FixtureSessionAuthority,
)
from cdit_support_mao.agents.coordinator.handoff import HandoffRegistry
from cdit_support_mao.agents.triage.anthropic_client import create_anthropic_client
from cdit_support_mao.agents.triage.anthropic_adapter import MODEL_ID, SYSTEM_PROMPT
from cdit_support_mao.agents.triage.runtime_harness import MannyA0A2Harness
from cdit_support_mao.contracts.common import CONTRACT_VERSION

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CASES = ROOT / "synthetic_data" / "evaluation_draft" / "v1" / "cases.json"
DEFAULT_REPORT = ROOT / "docs" / "lanes" / "manny" / "evaluation" / "EVAL-DRAFT-V1-LIVE-TRIAGE.md"
DEFAULT_RESULTS = ROOT / "docs" / "lanes" / "manny" / "evaluation" / "eval-draft-v1-live-triage.results.json"
POLICY_VERSION = "SYN-EVAL-TRIAGE-POLICY-V1"


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_case(case: dict[str, Any], *, client: Any, authorized: bool) -> dict[str, Any]:
    case_id = case["case_id"]
    message = case["source_message"]["text"]
    owner, sender, receiver = object(), object(), object()
    sessions = FixtureSessionAuthority(provisioning_capability=owner, ttl_seconds=3600)
    token = sessions.issue(
        FixtureSession(
            actor_id="SYN-ACTOR-EVAL-001",
            role="staff",
            active=True,
            allowed_case_ids=(case_id,),
        ),
        capability=owner,
    )
    versions = FixtureCaseVersions(provisioning_capability=owner)
    versions.set_version(case_id, 1, expected_version=None, capability=owner)
    policies = FixturePolicyVersions(
        provisioning_capability=owner,
        active=frozenset({POLICY_VERSION}),
    )
    coordinator = Coordinator(sessions, case_versions=versions, policy_versions=policies)
    registry = HandoffRegistry(
        sender_capability=sender,
        receiver_capability=receiver,
        timeout_seconds=60,
        actor_sessions=sessions,
        case_versions=versions,
        policy_versions=policies,
    )
    harness = MannyA0A2Harness(
        coordinator,
        registry,
        sender_capability=sender,
        receiver_capability=receiver,
    )
    request = {
        "case_id": case_id,
        "case_version": 1,
        "policy_version": POLICY_VERSION,
        "message": message,
        "data_classification": "synthetic",
    }
    run_id = f"LIVE-{uuid4()}"
    started_at = datetime.now(UTC)
    result = harness.run(
        request,
        session_token=token,
        client=client,
        billable_call_authorized=authorized,
        now=started_at,
    )
    ended_at = datetime.now(UTC)
    triage = result.triage
    expected_items = case["items"]
    actual_items = tuple(triage.candidate.items) if triage is not None else ()
    expected_by_index = {item["item_index"]: item for item in expected_items}
    actual_by_index = {item.item_index: item for item in actual_items}
    comparisons = []
    for index in sorted(set(expected_by_index) | set(actual_by_index)):
        expected = expected_by_index.get(index)
        actual = actual_by_index.get(index)
        expected_proposal = expected.get("triage_proposal", {}) if expected else {}
        actual_category = actual.category if actual else None
        actual_label = actual.category_label if actual else None
        has_semantic_output = triage is not None and triage.semantic_result is not None and actual is not None
        comparisons.append(
            {
                "item_index": index,
                "expected_category": expected_proposal.get("category") if expected else None,
                "expected_category_label": expected_proposal.get("label") if expected else None,
                "actual_category": actual_category,
                "actual_category_label": actual_label,
                "category_match": (
                    expected_proposal.get("category") == actual_category
                    and expected_proposal.get("label") == actual_label
                    if has_semantic_output and expected is not None and actual is not None else None
                ),
                "expected_span": expected.get("source_span") if expected else None,
                "actual_span": (
                    {"start": actual.source_start, "end": actual.source_end} if actual else None
                ),
                "span_match": (
                    expected.get("source_span")
                    == {"start": actual.source_start, "end": actual.source_end}
                    if expected is not None and actual is not None else False
                ),
                "evidence_quote_sha256": (
                    _sha256(actual.category_evidence_quote.encode("utf-8"))
                    if actual is not None and actual.category_evidence_quote else None
                ),
            }
        )

    semantic = triage.semantic_result if triage is not None else None
    output_items = semantic.proposal.items if semantic is not None else ()
    model_call_count = 1 if semantic is not None else 0
    return {
        "case_id": case_id,
        "trace_id": result.intake.trace_id,
        "run_id": (
            result.intake.context.run_id
            if result.intake.context is not None
            else run_id
        ),
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "input_sha256": _sha256(message.encode("utf-8")),
        "intake_status": result.intake.status.value,
        "intake_checkpoint": result.intake.checkpoint,
        "intake_reason_code": result.intake.reason_code,
        "handoff_events": [
            {
                "event": event.event,
                "status": event.status,
                "owner": event.owner,
                "sequence": event.sequence,
                "state_version": event.state_version,
                "timestamp": event.timestamp.isoformat(),
            }
            for event in result.events
        ],
        "triage_status": triage.status if triage is not None else None,
        "triage_reason": triage.reason if triage is not None else None,
        "urgency": triage.urgency if triage is not None else None,
        "destination": triage.destination if triage is not None else None,
        "human_review_required": (
            triage.human_review_required if triage is not None else None
        ),
        "downstream_allowed": triage.downstream_allowed if triage is not None else None,
        "dispatched": triage.dispatched if triage is not None else None,
        "model_call_count": model_call_count,
        "model": semantic.model if semantic is not None else None,
        "prompt_id": semantic.prompt_id if semantic is not None else None,
        "prompt_sha256": semantic.system_prompt_sha256 if semantic is not None else _sha256(SYSTEM_PROMPT.encode("utf-8")),
        "request_payload_sha256": semantic.request_payload_sha256 if semantic is not None else None,
        "input_tokens": semantic.input_tokens if semantic is not None else None,
        "output_tokens": semantic.output_tokens if semantic is not None else None,
        "model_elapsed_ms": semantic.elapsed_ms if semantic is not None else None,
        "item_count_expected": len(expected_items),
        "item_count_actual": len(actual_items),
        "items": comparisons,
        "urgency_contract_pass": (
            triage.urgency == "unknown" and all(item.urgency == "unknown" for item in output_items)
            if semantic is not None and triage is not None else None
        ),
        "human_review_contract_pass": (
            triage.human_review_required is True
            and triage.downstream_allowed is False
            and triage.dispatched is False
            if triage is not None else None
        ),
    }


def run_batch(
    cases_path: Path,
    *,
    case_ids: set[str] | None,
    max_cases: int,
    client: Any,
    billable_call_authorized: bool,
) -> dict[str, Any]:
    dataset_bytes = cases_path.read_bytes()
    dataset = json.loads(dataset_bytes.decode("utf-8"))
    cases = dataset.get("cases")
    if not isinstance(cases, list) or len(cases) != dataset.get("case_count"):
        raise ValueError("evaluation_case_count_mismatch")
    if dataset.get("scope", {}).get("synthetic_only") is not True:
        raise ValueError("evaluation_dataset_not_marked_synthetic_only")
    selected = [case for case in cases if case_ids is None or case["case_id"] in case_ids]
    if case_ids is not None and {case["case_id"] for case in selected} != case_ids:
        raise ValueError("requested_case_id_not_in_dataset")
    if not selected or len(selected) > max_cases:
        raise ValueError("selected_case_count_outside_limit")

    case_results = []
    for case in selected:
        case_results.append(
            _run_case(case, client=client, authorized=billable_call_authorized)
        )

    scored_items = [
        item
        for case in case_results
        for item in case["items"]
        if item["category_match"] is not None
    ]
    proposal_items = [
        item for item in scored_items
        if item["actual_category"] is not None and item["expected_category"] is not None
    ]
    category_matches = sum(item["category_match"] is True for item in proposal_items)
    abstention_items = [item for item in scored_items if item["actual_category"] is None]
    span_checked = [
        item for item in scored_items
        if item["expected_span"] is not None and item["actual_span"] is not None
    ]
    span_matches = sum(item["span_match"] for item in span_checked)
    calls = sum(case["model_call_count"] for case in case_results)
    tokens_in = sum(case["input_tokens"] or 0 for case in case_results)
    tokens_out = sum(case["output_tokens"] or 0 for case in case_results)
    return {
        "run_id": f"CDIT-LIVE-EVAL-{uuid4()}",
        "generated_at": datetime.now(UTC).isoformat(),
        "dataset_id": dataset["dataset_id"],
        "dataset_sha256": _sha256(dataset_bytes.replace(b"\r\n", b"\n")),
        "dataset_status": dataset.get("status"),
        "label_approval": dataset.get("approval", {}),
        "diagnostic_only": not bool(dataset.get("approval", {}).get("approved") and dataset.get("approval", {}).get("scoring_authorized")),
        "model": MODEL_ID,
        "contract_version": CONTRACT_VERSION,
        "system_prompt_sha256": _sha256(SYSTEM_PROMPT.encode("utf-8")),
        "cases_selected": len(selected),
        "items_expected": sum(len(case["items"]) for case in selected),
        "model_calls": calls,
        "model_call_attempts_verified": False,
        "model_call_attempts_note": "model_calls counts validated semantic results; failed SDK attempts are not instrumented by this runner",
        "model_calls_authorized": billable_call_authorized,
        "model_calls_sequential": True,
        "retry_count": 0,
        "ticket_writes": 0,
        "external_dispatches": 0,
        "input_tokens_total": tokens_in,
        "output_tokens_total": tokens_out,
        "triage_category": {
            "scored_items": len(proposal_items),
            "matches": category_matches,
            "accuracy": category_matches / len(proposal_items) if proposal_items else None,
            "proposal_disagreements": len(proposal_items) - category_matches,
            "abstentions_with_expected_outputs": len(abstention_items),
            "unpaired_actual_items": sum(
                item["expected_category"] is None and item["actual_category"] is not None
                for case in case_results for item in case["items"]
            ),
            "unscored_items": sum(len(case["items"]) for case in case_results) - len(scored_items),
        },
        "segmentation": {
            "checked_items": len(span_checked),
            "matching_spans": span_matches,
            "span_match_rate": span_matches / len(span_checked) if span_checked else None,
        },
        "cases": case_results,
        "other_gates": {
            "knowledge": "see separate non-billable Knowledge diagnostic",
            "auditor_band_and_route": "not_scored_by_triage_runtime",
            "troubleshooting": "not_run",
            "documentation": "not_run",
            "full_mao": "not_run",
            "actual_model_cost": "not_calculated",
        },
    }


def render_report(result: dict[str, Any]) -> str:
    triage = result["triage_category"]
    spans = result["segmentation"]
    accuracy = triage["accuracy"]
    accuracy_text = "N/A" if accuracy is None else f"{accuracy:.1%}"
    span_rate = spans["span_match_rate"]
    span_text = "N/A" if span_rate is None else f"{span_rate:.1%}"
    lines = [
        "# Synthetic live Triage diagnostic",
        "",
        "**Diagnostic only.** This report records real, billable Claude Sonnet 5.5 calls on synthetic cases. It does not approve draft labels or represent full MAO accuracy.",
        "",
        f"- Batch run: {result['run_id']}",
        f"- Started/report time: {result['generated_at']}",
        f"- Dataset: {result['dataset_id']} ({result['dataset_status']})",
        f"- Dataset SHA-256: {result['dataset_sha256']}",
        f"- Label approval flags: approved={result['label_approval'].get('approved')}, scoring_authorized={result['label_approval'].get('scoring_authorized')}",
        f"- Cases/items selected: {result['cases_selected']} / {result['items_expected']}",
        f"- Validated model responses: {result['model_calls']} (SDK attempt count is not instrumented; retries are configured off; authorized={result['model_calls_authorized']}, sequential={result['model_calls_sequential']})",
        f"- Model / contract: {result['model']} / {result['contract_version']}",
        f"- Input/output tokens: {result['input_tokens_total']} / {result['output_tokens_total']}",
        "",
        "## Observed Triage results",
        "",
        f"- Category proposals paired with an expected item: {triage['matches']}/{triage['scored_items']} matched ({accuracy_text}); {triage.get('proposal_disagreements', 0)} differed from the draft expectation.",
        f"- Abstentions with expected outputs: {triage.get('abstentions_with_expected_outputs', 0)}; unpaired extra model items: {triage.get('unpaired_actual_items', 0)}; expected items without a validated result: {triage['unscored_items']}.",
        f"- Item spans: {spans['matching_spans']}/{spans['checked_items']} matched ({span_text}).",
        "",
        "No urgency or destination accuracy is calculated: the A2 contract requires both to remain Unknown until human review. Auditor band/route decisions are also not scored by this run.",
        "",
        "| Case | Trace ID | Intake | Triage | Calls | Category matches |",
        "| :--- | :--- | :--- | :--- | ---: | :--- |",
    ]
    for case in result["cases"]:
        matches = [
            item for item in case["items"]
            if item["category_match"] is not None
            and item["expected_category"] is not None
            and item["actual_category"] is not None
        ]
        correct = sum(item["category_match"] is True for item in matches)
        lines.append(
            f"| {case['case_id']} | {case['trace_id']} | {case['intake_status']} | "
            f"{case['triage_status'] or 'not reached'} | {case['model_call_count']} | "
            f"{correct}/{len(matches)} |"
        )
    lines += ["", "## Limits", ""]
    lines.extend(f"- {name}: {value}" for name, value in result["other_gates"].items())
    lines += [
        "",
        "No raw case text, API key, model rationale, or unredacted prompt payload is stored in this report. Input and evidence are identified by hashes.",
    ]
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run sequential, explicitly authorized live Triage calls on synthetic evaluation cases."
    )
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--case-ids", help="Comma-separated exact case IDs; omit to select the full dataset.")
    parser.add_argument("--max-cases", type=int, required=True, help="Hard cap for case runs in this invocation.")
    parser.add_argument(
        "--authorize-billable-calls",
        action="store_true",
        help="Explicitly authorize one billable provider call per eligible selected case; no retries.",
    )
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    args = parser.parse_args(argv)
    if not args.authorize_billable_calls:
        parser.error("billable calls require --authorize-billable-calls")
    if type(args.max_cases) is not int or not 1 <= args.max_cases <= 100:
        parser.error("--max-cases must be between 1 and 100")
    ids = None if not args.case_ids else {value.strip() for value in args.case_ids.split(",") if value.strip()}
    if ids is not None and (len(ids) != len([x for x in args.case_ids.split(",") if x.strip()]) or len(ids) > args.max_cases):
        parser.error("case IDs must be unique and within --max-cases")

    client = create_anthropic_client()
    result = run_batch(
        args.cases,
        case_ids=ids,
        max_cases=args.max_cases,
        client=client,
        billable_call_authorized=True,
    )
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.results.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(render_report(result), encoding="utf-8", newline="\n")
    args.results.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(
        f"LIVE DIAGNOSTIC: {result['cases_selected']} cases, {result['model_calls']} model calls; "
        f"Triage category {result['triage_category']['matches']}/{result['triage_category']['scored_items']}."
    )
    print(f"Report: {args.report}")
    print(f"Results: {args.results}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
