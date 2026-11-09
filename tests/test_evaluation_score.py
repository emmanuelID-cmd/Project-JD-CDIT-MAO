from datetime import date
from types import SimpleNamespace

from cdit_support_mao.evaluation_score import summarize


def test_summary_reports_item_level_knowledge_diagnostic_without_approving_labels():
    run = SimpleNamespace(
        evaluation_as_of=date(2026, 11, 10),
        source_set_version="SYN-EVAL-SOURCE-SET",
        knowledge_agent_version="0.2.0",
        source_map_problems=(),
        items=(
            SimpleNamespace(
                case_id="SYN-EVAL-001",
                item_id="SYN-EVAL-001-I1",
                scenario="routine",
                route="knowledge",
                expected=("KB-EXAMPLE#s1 v1.0",),
                knowledge_status="completed",
                reason_codes=(),
                cited=("KB-EXAMPLE#s1 v1.0",),
                verdict="cited_expected",
            ),
            SimpleNamespace(
                case_id="SYN-EVAL-067",
                item_id="SYN-EVAL-067-I1",
                scenario="stale-source",
                route="knowledge",
                expected=("KB-STALE#s1 v1.0",),
                knowledge_status="completed",
                reason_codes=(),
                cited=("KB-OTHER#s1 v1.0",),
                verdict="cited_other_source",
            ),
            SimpleNamespace(
                case_id="SYN-EVAL-051",
                item_id="SYN-EVAL-051-I1",
                scenario="ambiguous",
                route="auditor",
                expected=(),
                knowledge_status=None,
                reason_codes=(),
                cited=(),
                verdict="held_for_auditor",
            ),
        ),
    )
    dataset = {
        "dataset_id": "SYNTHETIC-DRAFT",
        "status": "DRAFT_NOT_APPROVED",
        "approval": {"approved": False, "scoring_authorized": False},
        "cases": [{}, {}, {}],
    }
    source_map = SimpleNamespace(
        by_citation=lambda: {
            "KB-EXAMPLE#s1 v1.0": SimpleNamespace(
                citation="KB-EXAMPLE#s1 v1.0",
                expected_outcome="cited",
            ),
            "KB-STALE#s1 v1.0": SimpleNamespace(
                citation="KB-STALE#s1 v1.0",
                expected_outcome="abstain_stale",
            ),
        }
    )

    result = summarize(run, dataset, source_map)

    assert result["diagnostic_only"] is True
    assert result["final_evaluation_score"] is None
    assert result["case_count"] == 3
    assert result["item_count"] == 3
    assert result["approval"] == {"approved": False, "scoring_authorized": False}
    assert result["knowledge_metrics"]["expected_citation_rate"] == 1.0
    assert result["knowledge_metrics"]["expected_abstention_cases"] == 1
    assert result["knowledge_metrics"]["stale_source_cases"] == 1
    assert result["knowledge_metrics"]["stale_source_cases_without_an_answer"] == 0
    assert result["knowledge_metrics"]["wrong_source_or_missing_expected_abstention"] == 1
    assert result["knowledge_metrics"]["auditor_held_items"] == 1
    assert "semantic triage category accuracy" in result["not_scored_gates"]
