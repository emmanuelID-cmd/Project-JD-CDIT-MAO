"""Synthetic Manny-owned A0–A2 runtime harness.

This harness composes Coordinator intake and its acknowledged handoff with the
Triage runtime. It remains the provider-injected A0–A2 building block; the
connected A0–A3 entry point is in ``combined_harness.run_manny_connected``.
It does not construct a model client, load credentials, persist data, or
perform external actions.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from cdit_support_mao.agents.coordinator import Coordinator
from cdit_support_mao.agents.coordinator.handoff import (
    HandoffError,
    HandoffCheckpoint,
    HandoffEvent,
    HandoffRegistry,
)
from cdit_support_mao.agents.coordinator.intake import IntakeResult, IntakeStatus
from cdit_support_mao.agents.triage.anthropic_adapter import AnthropicClient
from cdit_support_mao.agents.triage.attention import FixtureAttentionPatterns
from cdit_support_mao.agents.triage.development_examples import (
    DevelopmentCatalogError,
    load_project_category_taxonomy,
)
from cdit_support_mao.agents.triage.runtime import TriageRuntimeResult, run_triage_runtime


@dataclass(frozen=True, slots=True)
class MannyA0A2Run:
    """One process-local synthetic intake through the Triage A2 boundary."""

    intake: IntakeResult
    acknowledged_handoff: HandoffCheckpoint | None
    triage: TriageRuntimeResult | None
    events: tuple[HandoffEvent, ...]

    @property
    def status(self) -> str:
        if self.triage is not None:
            return self.triage.status
        return self.intake.status.value


class MannyA0A2Harness:
    """Compose Coordinator intake and Manny's runtime without downstream handoff."""

    def __init__(
        self,
        coordinator: Coordinator,
        registry: HandoffRegistry,
        *,
        sender_capability: object,
        receiver_capability: object,
        fixture_patterns: FixtureAttentionPatterns | None = None,
    ) -> None:
        self._coordinator = coordinator
        self._registry = registry
        self._sender_capability = sender_capability
        self._receiver_capability = receiver_capability
        self._fixture_patterns = fixture_patterns

    def run(
        self,
        request: object,
        *,
        session_token: object,
        client: AnthropicClient | None = None,
        billable_call_authorized: bool = False,
        now: datetime | None = None,
    ) -> MannyA0A2Run:
        """Run synthetic intake and stop at a review-only A2 result.

        A client and explicit per-run authorization are both required before
        the semantic adapter can call a provider. No default client or key
        lookup is performed here.
        """
        intake = self._coordinator.prepare(request, session_token=session_token)
        if intake.status is not IntakeStatus.READY_FOR_TRIAGE or intake.context is None:
            return MannyA0A2Run(intake, None, None, ())

        prepared = self._registry.prepare(
            intake,
            capability=self._sender_capability,
            session_token=session_token,
            now=now,
        )
        accepted = self._registry.acknowledge(
            prepared.handoff_id,
            expected_version=prepared.state_version,
            capability=self._receiver_capability,
            context=intake.context,
            now=now,
        )
        try:
            taxonomy = load_project_category_taxonomy()
        except DevelopmentCatalogError:
            taxonomy = None
        triage = run_triage_runtime(
            self._registry,
            handoff_id=accepted.handoff_id,
            expected_version=accepted.state_version,
            receiver_capability=self._receiver_capability,
            context=intake.context,
            category_taxonomy=taxonomy,
            fixture_patterns=self._fixture_patterns,
            client=client,
            billable_call_authorized=billable_call_authorized,
            now=now,
        )
        events = tuple(
            event for event in self._registry.events()
            if event.run_id == intake.context.run_id
        )
        return MannyA0A2Run(intake, accepted, triage, events)

    def source_is_current(self, run: MannyA0A2Run, *, now: datetime | None = None) -> bool:
        """Revalidate the exact acknowledged A0/A1 source before each later stage."""
        if run.acknowledged_handoff is None or run.intake.context is None or run.triage is None:
            return False
        try:
            self._registry.validate_active(
                run.acknowledged_handoff.handoff_id,
                expected_version=run.acknowledged_handoff.state_version,
                capability=self._receiver_capability,
                context=run.intake.context,
                now=now,
            )
        except HandoffError:
            return False
        return True
