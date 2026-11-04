"""Synthetic lane evaluation set: expected outcomes plus invariants that must hold for every case."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from cdit_support_mao.contracts import AgentStatus, ClaimLabel
from cdit_support_mao.lane_harness import case_files, check_expectations, load_case, main

from conftest import CASES_DIR, NOW, REPO_ROOT

CASES = case_files(CASES_DIR)


def test_case_set_covers_prd_scenarios() -> None:
    assert len(CASES) >= 12
    refs = " ".join(load_case(path).scenario_ref for path in CASES)
    for needed in ("eval case 1", "eval case 2", "eval case 3", "injection", "Protect sensitive data"):
        assert needed in refs


@pytest.mark.parametrize("path", CASES, ids=[p.stem for p in CASES])
def test_case_matches_expected_outcome(harness, policy, path: Path) -> None:
    run = harness.run(load_case(path), now=NOW)
    assert check_expectations(run) == []

    contributions = [run.knowledge, run.troubleshooting, run.documentation]
    for contribution in contributions:
        assert contribution.human_review_required is True
        assert contribution.context == run.context
        for claim in contribution.claims:
            if claim.label is ClaimLabel.VERIFIED:
                assert claim.sources
    # Provenance chain: each stage records what it consumed.
    assert run.triage.contribution_id in {r.contribution_id for r in run.knowledge.input_refs}
    assert {run.triage.contribution_id, run.knowledge.contribution_id} <= {
        r.contribution_id for r in run.troubleshooting.input_refs
    }
    # A4 boundary: nothing outside Tier 1 is ever suggested.
    for step in run.troubleshooting.steps:
        assert policy.classify(step.action_type) == "tier1"
    # Downstream confidence never exceeds upstream.
    order = {"low": 0, "medium": 1, "high": 2}
    assert order[run.troubleshooting.confidence] <= order[run.knowledge.confidence]
    if run.documentation.status is AgentStatus.COMPLETED:
        assert order[run.documentation.confidence] <= order[run.troubleshooting.confidence]
        assert "no ticket state changed" in run.documentation.draft.rendered_text


def test_harness_cli_passes_on_case_set(capsys) -> None:
    assert main([str(CASES_DIR)]) == 0
    assert f"{len(CASES)} passed, 0 failed" in capsys.readouterr().out


FORBIDDEN_IMPORTS = {"socket", "requests", "httpx", "urllib", "http", "smtplib", "subprocess", "aiohttp"}


def test_agents_have_no_network_or_process_access() -> None:
    """UC-07 boundary: Shawn's Lane agents cannot send, fetch, or execute anything."""
    agent_dir = REPO_ROOT / "src" / "cdit_support_mao" / "agents"
    for path in agent_dir.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            for name in names:
                assert name.split(".")[0] not in FORBIDDEN_IMPORTS, f"{path.name} imports {name}"
