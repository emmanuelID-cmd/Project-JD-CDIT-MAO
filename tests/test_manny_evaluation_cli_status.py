"""CLI contract: fixture success remains preliminary, not Phase 4 acceptance."""

import json
from pathlib import Path

from cdit_support_mao.manny_evaluation import main


def test_cli_returns_preliminary_status_and_persists_not_scored_metadata(
    tmp_path: Path, capsys
) -> None:
    report_path = tmp_path / "report.md"
    results_path = tmp_path / "results.json"

    exit_code = main(["--report", str(report_path), "--results", str(results_path)])

    assert exit_code == 2
    assert "PHASE 4 IS NOT READY OR SCORED" in capsys.readouterr().out
    assert "NOT READY" in report_path.read_text(encoding="utf-8")

    results = json.loads(results_path.read_text(encoding="utf-8"))
    assert results["end_to_end"]["fixture_assertions_passed"] is True
    assert results["end_to_end"]["phase_exit_ready"] is False
    assert results["end_to_end"]["scoring_status"] == "not_scored"
    assert results["end_to_end"]["labeled_cases_evaluated"] == 0
