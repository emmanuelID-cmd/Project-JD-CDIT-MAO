"""Shared fixtures for Shawn's Lane agent tests (synthetic data only)."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from cdit_support_mao.agents.knowledge import KnowledgeAgent, KnowledgeCorpus, load_corpus
from cdit_support_mao.agents.troubleshooting import (
    TroubleshootingAgent,
    TroubleshootingPolicy,
    load_policy,
)
from cdit_support_mao.contracts import (
    AgentStatus,
    CaseFact,
    CheckpointOutcome,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    SourceKind,
    SourceRef,
    TriageHandoff,
)
from cdit_support_mao.lane_harness import LaneHarness

REPO_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_DIR = REPO_ROOT / "synthetic_data" / "knowledge"
POLICY_PATH = REPO_ROOT / "synthetic_data" / "policy" / "troubleshooting-policy_v0.1.2.json"
CASES_DIR = REPO_ROOT / "synthetic_data" / "cases"

AS_OF = date(2026, 11, 3)
NOW = datetime(2026, 11, 3, 15, 0, tzinfo=UTC)


@pytest.fixture(scope="session")
def corpus() -> KnowledgeCorpus:
    return load_corpus(KNOWLEDGE_DIR)


@pytest.fixture(scope="session")
def policy() -> TroubleshootingPolicy:
    return load_policy(POLICY_PATH)


@pytest.fixture(scope="session")
def knowledge_agent(corpus: KnowledgeCorpus) -> KnowledgeAgent:
    return KnowledgeAgent(corpus)


@pytest.fixture(scope="session")
def troubleshooting_agent(policy: TroubleshootingPolicy) -> TroubleshootingAgent:
    return TroubleshootingAgent(policy)


@pytest.fixture(scope="session")
def harness(corpus: KnowledgeCorpus, policy: TroubleshootingPolicy) -> LaneHarness:
    return LaneHarness(corpus, policy)


@pytest.fixture
def context() -> RunContext:
    return RunContext(
        run_id="RUN-TEST-1",
        case_id="SYN-CASE-TEST",
        case_version=1,
        policy_version="SYN-SUPPORT-POLICY-0.1",
    )


@pytest.fixture
def make_triage(context: RunContext) -> Callable[..., TriageHandoff]:
    """Build a triage stand-in (fixture, not Manny's agent) for a summary."""

    def build(
        summary: str,
        *,
        product_area: str | None = None,
        facts: dict[str, tuple[str, bool]] | None = None,
        missing: tuple[str, ...] = (),
        status: AgentStatus = AgentStatus.COMPLETED,
        run_context: RunContext | None = None,
        contribution_id: str = "TRI-TEST",
    ) -> TriageHandoff:
        ctx = run_context or context
        passed = status is AgentStatus.COMPLETED
        return TriageHandoff(
            contribution_id=contribution_id,
            agent="triage-stand-in",
            agent_version="fixture",
            context=ctx,
            created_at=NOW,
            status=status,
            checkpoint=CheckpointOutcome(
                checkpoint="A2",
                passed=passed,
                reason_codes=() if passed else (ReasonCode.UPSTREAM_BLOCKED,),
            ),
            confidence=ConfidenceBand.HIGH,
            confidence_rationale="test fixture",
            case_summary=summary,
            product_area=product_area,
            category="test_category",
            category_confidence=ConfidenceBand.HIGH,
            urgency="low",
            case_facts=tuple(
                CaseFact(
                    field=field,
                    value=value,
                    verified=verified,
                    source=SourceRef(
                        kind=SourceKind.CASE_FIELD,
                        source_id=f"{ctx.case_id}.{field}",
                        version=str(ctx.case_version),
                    ),
                )
                for field, (value, verified) in (facts or {}).items()
            ),
            missing_facts=missing,
        )

    return build
