"""Developer fixture harness; not the held-out D-09 evaluation set."""
import json
from pathlib import Path
from cdit_support_mao.agents.coordinator.harness import FixtureSet, run_fixture_set

def test_synthetic_fixture_checks_pass_and_omit_message():
    path=Path("synthetic_data/manny_coordinator/intake_checks.json")
    fixtures=FixtureSet.model_validate_json(path.read_text(encoding="utf-8"))
    results=run_fixture_set(fixtures)
    assert len(results)==8 and all(item["passed"] for item in results)
    rendered=json.dumps(results)
    assert all(case.message not in rendered for case in fixtures.cases)

def test_incorrect_expected_status_is_reported_as_failure():
    path=Path("synthetic_data/manny_coordinator/intake_checks.json")
    fixtures=FixtureSet.model_validate_json(path.read_text(encoding="utf-8"))
    changed=fixtures.cases[0].model_copy(update={"expected_status":"rejected_input"})
    result=run_fixture_set(fixtures.model_copy(update={"cases":(changed,)}))
    assert result[0]["passed"] is False
