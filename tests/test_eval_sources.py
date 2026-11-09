"""Evaluation-only Knowledge fixtures, source map, and source check (Shawn's Lane).

Synthetic data only. The fixtures ground the 100-case evaluation draft; they must never
enter the runtime corpus, and their approval is test-only."""

from __future__ import annotations

import json
import re
import shutil
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from cdit_support_mao.agents.knowledge import (
    CorpusError,
    KnowledgeAgent,
    load_corpus,
    load_evaluation_corpus,
)
from cdit_support_mao.agents.knowledge.corpus import ineligibility_reason
from cdit_support_mao.contracts import RunContext
from cdit_support_mao.lane_eval_sources import (
    _stand_in,
    load_source_map,
    main,
    render_report,
    results_json,
    run_source_check,
    validate_source_map,
)

from conftest import KNOWLEDGE_DIR, REPO_ROOT

FIXTURES = REPO_ROOT / "synthetic_data" / "evaluation_knowledge" / "eval-draft-v1"
# The evaluation draft cites SYN-TS-POLICY 0.1.1; the source map is checked against that version.
POLICY_PATH = REPO_ROOT / "synthetic_data" / "policy" / "troubleshooting-policy_v0.1.1.json"
CASES = REPO_ROOT / "synthetic_data" / "evaluation_draft" / "v1" / "cases.json"
AS_OF = date(2026, 11, 10)
NOW = datetime(2026, 11, 10, 12, 0, tzinfo=UTC)
FIXTURE_IDS = {
    "KB-ACC-015", "KB-CMP-480", "KB-FRM-420", "KB-INC-450", "KB-PAY-400",
    "KB-PAY-410", "KB-PRV-470", "KB-SAF-460", "KB-SHF-440",
}
PLACEHOLDERS = {
    "SYN-AUDIT-EVIDENCE-PROCEDURE", "SYN-COMPLIANCE-INTAKE-POLICY", "SYN-EMPLOYEE-RECORD-PROCEDURE",
    "SYN-EXPORT-GUIDE-A", "SYN-EXPORT-GUIDE-B", "SYN-FORM-INDEX", "SYN-INCIDENT-INTAKE-POLICY",
    "SYN-MANUAL-FALLBACK-POLICY", "SYN-OUT-OF-SCOPE-POLICY", "SYN-PAY-DISCREPANCY-PROCEDURE",
    "SYN-PAY-STATEMENT-GUIDANCE", "SYN-PRIVACY-RESPONSE-POLICY", "SYN-ROLE-ACCESS-MATRIX",
    "SYN-SAFETY-ESCALATION-POLICY", "SYN-SCHEDULING-CONFLICT-PROCEDURE", "SYN-STALE-EXPORT-ARTICLE",
    "SYN-UNTRUSTED-CONTENT-RULE",
}
# Roles must be the application roles User, Staff, and Admin; no tiers from job titles.
NON_APP_ROLES = re.compile(
    r"support lead|payroll staff|coordinator|privacy contact|safety contact|administrator|"
    r"supervisor|manager|\bL2\b|tier 1 staff|hr (team|staff)",
    re.IGNORECASE,
)


@pytest.fixture(scope="module")
def evaluation():
    return load_evaluation_corpus(FIXTURES, KNOWLEDGE_DIR)


@pytest.fixture(scope="module")
def policy():
    from cdit_support_mao.agents.troubleshooting import load_policy

    return load_policy(POLICY_PATH)


def _run(corpus, text: str):
    context = RunContext(run_id="RUN-EVAL-TEST", case_id="SYN-CASE-EVAL", case_version=1, policy_version="P")
    result = KnowledgeAgent(corpus).run(
        context, _stand_in(context, text, NOW), acknowledged={"TRI-EVAL-SOURCE-CHECK"}, as_of=AS_OF, now=NOW
    )
    cited = [f"{p.source.source_id}#{p.source.locator} v{p.source.version}" for p in result.passages]
    return result.status.value, [code.value for code in result.checkpoint.reason_codes], cited


# --- Separation from the runtime corpus -------------------------------------------


def test_runtime_corpus_is_unchanged_and_excludes_fixtures() -> None:
    runtime = load_corpus(KNOWLEDGE_DIR)
    assert len(runtime.articles) == 38
    assert not {article.doc_id for article in runtime.articles} & FIXTURE_IDS


def test_evaluation_corpus_adds_the_fixture_set(evaluation) -> None:
    runtime = load_corpus(KNOWLEDGE_DIR)
    again = load_evaluation_corpus(FIXTURES, KNOWLEDGE_DIR)
    assert len(evaluation.corpus.articles) == 38 + 9
    assert evaluation.fixture_doc_ids == FIXTURE_IDS
    assert evaluation.corpus.source_set_version == again.corpus.source_set_version
    assert evaluation.corpus.source_set_version != runtime.source_set_version
    assert re.fullmatch(r"SRC-[0-9A-F]{12}", evaluation.corpus.source_set_version)
    manifest = evaluation.manifest
    assert (manifest.use, manifest.data_classification) == ("evaluation_only", "synthetic")
    assert manifest.evaluation_as_of == AS_OF
    assert "not CDIT policy" in manifest.notice and "User, Staff, and Admin" in manifest.notice


def test_load_corpus_refuses_a_fixture_set_folder() -> None:
    for folder in (FIXTURES, FIXTURES / "articles"):
        with pytest.raises(CorpusError, match="evaluation-only fixtures"):
            load_corpus(folder)


def test_fixture_set_needs_a_valid_manifest(tmp_path: Path) -> None:
    target = tmp_path / "set"
    shutil.copytree(FIXTURES, target)
    (target / "manifest.json").unlink()
    with pytest.raises(CorpusError, match="manifest not found"):
        load_evaluation_corpus(target, KNOWLEDGE_DIR)
    manifest = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))
    manifest["use"] = "runtime"
    (target / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(CorpusError, match="invalid evaluation fixture manifest"):
        load_evaluation_corpus(target, KNOWLEDGE_DIR)


def test_fixture_may_not_reuse_a_runtime_doc_id(tmp_path: Path) -> None:
    target = tmp_path / "set"
    shutil.copytree(FIXTURES, target)
    path = target / "articles" / "KB-FRM-420_v1.0.json"
    article = json.loads(path.read_text(encoding="utf-8"))
    article["doc_id"] = "KB-NAV-001"
    path.write_text(json.dumps(article), encoding="utf-8")
    with pytest.raises(CorpusError, match="reuse base doc_ids: KB-NAV-001"):
        load_evaluation_corpus(target, KNOWLEDGE_DIR)


# --- Fixture content -----------------------------------------------------------------


def test_fixtures_are_test_only_current_and_use_application_roles(evaluation, policy) -> None:
    known_actions = set(policy.tier1_action_types) | set(policy.staff_only_action_types)
    fixtures = [a for a in evaluation.corpus.articles if a.doc_id in evaluation.fixture_doc_ids]
    assert len(fixtures) == 9
    for article in fixtures:
        assert article.status == "approved" and article.data_classification == "synthetic"
        assert "test-only" in article.owner and "not CDIT policy" in article.owner
        assert ineligibility_reason(article, AS_OF) is None
        texts = [article.title]
        for section in article.sections:
            texts += [section.heading, section.text]
            texts += [step.text for step in section.steps]
            texts += [need.prompt for need in section.information_needed]
            texts += [stop.text for stop in section.stop_conditions]
            assert {step.action_type for step in section.steps} <= known_actions
        for text in texts:
            assert not NON_APP_ROLES.search(text), f"{article.doc_id}: non-application role in {text!r}"


def test_safety_fixture_is_a_human_handoff_without_medical_advice(evaluation) -> None:
    article = next(a for a in evaluation.corpus.articles if a.doc_id == "KB-SAF-460")
    section = article.sections[0]
    assert "cannot arrange emergency help or give medical advice" in section.text
    assert "Auditor review" in section.text
    assert any("Admin for human review" in stop.text for stop in section.stop_conditions)


def test_as_of_sits_inside_the_intended_freshness_window(evaluation) -> None:
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    assert date.fromisoformat(cases["evaluation_as_of"]) == AS_OF == evaluation.manifest.evaluation_as_of
    reasons = {(a.doc_id, a.version): ineligibility_reason(a, AS_OF) for a in evaluation.corpus.articles}
    intended = {
        ("KB-TRN-360", "1.0"): "source_stale",
        ("KB-RPT-040", "1.1"): "source_stale",
        ("KB-SCH-340", "1.0"): "source_not_effective",
        ("KB-NAV-001", "1.0"): "source_retired",
        ("KB-MOB-260", "1.4"): "source_retired",
        ("KB-DRAFT-060", "0.1"): "source_unapproved",
        ("KB-EDC-350", "0.2"): "source_unapproved",
    }
    actual = {key: reason.value for key, reason in reasons.items() if reason is not None}
    assert actual == intended


# --- Source map ----------------------------------------------------------------------


def test_source_map_matches_corpus_policy_and_manifest(evaluation, policy) -> None:
    source_map = load_source_map(FIXTURES)
    assert validate_source_map(source_map, evaluation, policy) == []
    placeholders = [p for entry in source_map.entries for p in entry.placeholder_ids]
    assert sorted(placeholders) == sorted(PLACEHOLDERS)


def test_source_map_validation_catches_drift(evaluation, policy) -> None:
    source_map = load_source_map(FIXTURES)
    entries = list(source_map.entries)
    entries[0] = entries[0].model_copy(update={"review_due": date(2026, 1, 1)})
    stale = source_map.model_copy(update={"entries": tuple(entries)})
    assert any("status or dates differ" in p for p in validate_source_map(stale, evaluation, policy))


def test_every_case_citation_is_in_the_source_map() -> None:
    known = set(load_source_map(FIXTURES).by_citation())
    cases = json.loads(CASES.read_text(encoding="utf-8"))["cases"]
    cited = {c for case in cases for c in case["evidence_expectations"]["expected_source_ids"]}
    assert cited <= known, sorted(cited - known)


# --- Retrieval -----------------------------------------------------------------------


@pytest.mark.parametrize(
    ("query", "citation"),
    [
        ("I cannot find the pay statement for the most recent completed pay period.", "KB-PAY-400#s1 v1.0"),
        ("correct the pay-statement email address on my profile", "KB-PAY-400#s2 v1.0"),
        ("Please send me a blank copy of the standard employee update form.", "KB-FRM-420#s1 v1.0"),
        ("Please resend the blank leave form", "KB-FRM-420#s1 v1.0"),
        ("A worker reports an injury and asks the support desk to arrange immediate help at the site.",
         "KB-SAF-460#s1 v1.0"),
        ("A synthetic User asks to view an Admin-only access audit screen.", "KB-ACC-015#s1 v1.0"),
    ],
)
def test_fixture_is_retrieved_only_from_the_evaluation_corpus(evaluation, query: str, citation: str) -> None:
    status, reasons, cited = _run(evaluation.corpus, query)
    assert (status, reasons, cited[0]) == ("completed", [], citation)
    status, reasons, cited = _run(load_corpus(KNOWLEDGE_DIR), query)
    assert (status, reasons, cited) == ("abstained", ["weak_evidence"], [])


@pytest.mark.parametrize(
    ("query", "reason"),
    [
        ("How can I download my training transcript?", "stale_source_only"),
        ("What is the maximum file size for uploading a regulatory document?", "conflicting_sources"),
        ("How do I change the email notification settings for my account?", "retrieved_injection"),
    ],
)
def test_existing_unsafe_sources_still_abstain_in_the_evaluation_corpus(evaluation, query: str, reason: str) -> None:
    status, reasons, cited = _run(evaluation.corpus, query)
    assert (status, cited) == ("abstained", [])
    assert reason in reasons


# --- Source check --------------------------------------------------------------------


def _mini_cases(tmp_path: Path) -> Path:
    def item(case_id: str, index: int, text: str, category: str) -> dict:
        return {"item_id": f"{case_id}-I{index}", "item_index": index, "text": text,
                "triage_proposal": {"category": category}}

    def case(case_id: str, scenario: str, items: list, expected: list, dispatch: bool = True) -> dict:
        return {"case_id": case_id, "scenario_key": f"{scenario}-1", "items": items,
                "current_runtime_expectation": {"knowledge_dispatch_candidate": dispatch},
                "evidence_expectations": {"expected_source_ids": expected}}

    cases = [
        case("SYN-EVAL-901", "hit", [item("SYN-EVAL-901", 1,
             "I cannot find the pay statement for the most recent completed pay period.", "Pay")],
             ["KB-PAY-400#s1 v1.0"]),
        case("SYN-EVAL-902", "linked", [
            item("SYN-EVAL-902", 1, "Please resend the blank leave form", "Forms"),
            item("SYN-EVAL-902", 2, "correct the pay-statement email address on my profile", "unknown")],
             ["KB-FRM-420#s1 v1.0", "KB-PAY-400#s2 v1.0"]),
        case("SYN-EVAL-903", "stale", [item("SYN-EVAL-903", 1,
             "How can I download my training transcript?", "How-to")], ["KB-TRN-360#s1 v1.0"]),
        case("SYN-EVAL-904", "no-dispatch", [item("SYN-EVAL-904", 1,
             "My last payslip seems lower than my timesheet suggests.", "Pay")],
             ["KB-PAY-410#s1 v1.0"], dispatch=False),
        case("SYN-EVAL-905", "policy", [item("SYN-EVAL-905", 1,
             "Should I change a medication dose?", "Wellbeing")], ["SYN-TS-POLICY 0.1.1 RR-04"]),
    ]
    path = tmp_path / "cases.json"
    path.write_text(json.dumps({"dataset_id": "CDIT-SYNTHETIC-EVALUATION-DRAFT-100-v1",
                                "evaluation_as_of": "2026-11-10", "cases": cases}), encoding="utf-8")
    return path


def test_source_check_routes_by_category_and_grades_results(tmp_path: Path) -> None:
    run = run_source_check(_mini_cases(tmp_path), FIXTURES, POLICY_PATH, KNOWLEDGE_DIR)
    verdicts = {item.item_id: item.verdict for item in run.items}
    assert verdicts == {
        "SYN-EVAL-901-I1": "cited_expected",
        "SYN-EVAL-902-I1": "cited_expected",
        "SYN-EVAL-902-I2": "held_for_auditor",
        "SYN-EVAL-903-I1": "abstained_as_expected",
        "SYN-EVAL-904-I1": "missed_abstained",
        "SYN-EVAL-905-I1": "no_source_expected_abstained",
    }
    held = next(item for item in run.items if item.item_id == "SYN-EVAL-902-I2")
    assert (held.route, held.knowledge_status) == ("auditor", None)
    notes = {note.case_id: note.note for note in run.case_notes}
    assert "KB-PAY-400#s2 v1.0 cannot be reached at A2" in notes["SYN-EVAL-902"]
    assert "knowledge_dispatch_candidate is false" in notes["SYN-EVAL-904"]
    assert run.source_map_problems == ()
    assert "| `held_for_auditor` | 1 |" in render_report(run)
    assert json.loads(results_json(run))["verdicts"]["cited_expected"] == 2


def test_source_check_fails_on_an_unmapped_citation(tmp_path: Path) -> None:
    path = _mini_cases(tmp_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["cases"][0]["evidence_expectations"]["expected_source_ids"] = ["KB-NOPE-999#s1 v1.0"]
    path.write_text(json.dumps(data), encoding="utf-8")
    run = run_source_check(path, FIXTURES, POLICY_PATH, KNOWLEDGE_DIR)
    assert run.items[0].verdict == "unmapped_citation"
    assert main(["--cases", str(path), "--fixtures", str(FIXTURES), "--policy", str(POLICY_PATH),
                 "--knowledge-dir", str(KNOWLEDGE_DIR)]) == 1


def test_source_check_on_the_evaluation_draft_keeps_routing_and_safety_invariants() -> None:
    run = run_source_check(CASES, FIXTURES, POLICY_PATH, KNOWLEDGE_DIR)
    assert run.source_map_problems == ()
    assert all(item.verdict != "unmapped_citation" for item in run.items)
    for item in run.items:
        assert (item.route == "auditor") == (item.category == "unknown")
    # Knowledge never answers an item for which no source is expected.
    assert all(item.verdict != "answered_without_expected_source" for item in run.items)
