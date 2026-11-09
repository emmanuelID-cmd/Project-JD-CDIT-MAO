"""Knowledge agent (Shawn's Lane) — PRD checkpoint A3, retrieval handoff.

Returns only approved, current, versioned passages with source references, or
abstains. It never synthesizes product guidance: passages are returned verbatim
as untrusted evidence. Abstention triggers: no relevant source, weak evidence,
only stale/unapproved sources, conflicting sources or versions, and
instruction-like content in retrieved text.

A Triage handoff may carry one linked item of a multi-item case message
(``item_scope``). Knowledge then re-checks the item's eligibility, retrieves on
the item text only, and echoes the item identity (``item_scope_ref``); it never
reads or repeats the category, urgency, attention, or Auditor values.
"""

from __future__ import annotations

from collections.abc import Set
from datetime import date, datetime

from cdit_support_mao.agents._gates import item_scope_reasons, unique, upstream_reasons, utc_now
from cdit_support_mao.agents.knowledge.corpus import (
    KbArticle,
    KnowledgeCorpus,
    ineligibility_reason,
)
from cdit_support_mao.agents.knowledge.injection import scan_for_injection
from cdit_support_mao.agents.knowledge.retrieval import LexicalIndex, ScoredSection
from cdit_support_mao.contracts.common import (
    PROVISIONAL_BAND_THRESHOLDS,
    AgentStatus,
    CheckpointOutcome,
    Claim,
    ClaimLabel,
    ConfidenceBand,
    ReasonCode,
    RunContext,
    SourceKind,
    SourceRef,
    band_for,
    stable_id,
)
from cdit_support_mao.contracts.handoffs import (
    EvidencePassage,
    ExcludedSource,
    InjectionFlag,
    KnowledgeResult,
    PassageInformationItem,
    PassageStep,
    PassageStopCondition,
    SourceConflict,
    TriageHandoff,
)

AGENT_NAME = "knowledge-agent"
# 0.3.0 (2026-11-09, L-1): query tokens that contain a digit are case identifiers and no
# longer count as topic terms in the relevance gate. Cut-offs are unchanged (D-08).
# 0.4.0 (2026-11-09, L-1/L-2 batch 2): courtesy words are not topic terms either, and the
# ineligible-anchor guard withholds an off-topic answer when the request's most specific
# word appears only in an ineligible source.
AGENT_VERSION = "0.4.0"
MAX_PASSAGES = 3
MIN_MATCHED_TERMS = 2

_STALE_REASONS = {ReasonCode.SOURCE_STALE, ReasonCode.SOURCE_NOT_EFFECTIVE}
_UNCALIBRATED = "Confidence thresholds are provisional and uncalibrated (D-08)."


def kb_section_ref(article: KbArticle, section_id: str) -> SourceRef:
    return SourceRef(
        kind=SourceKind.KB_SECTION,
        source_id=article.doc_id,
        version=article.version,
        locator=section_id,
    )


class KnowledgeAgent:
    """Retrieves approved evidence for a triaged case, or abstains."""

    def __init__(self, corpus: KnowledgeCorpus, *, min_relevance: float | None = None) -> None:
        """``min_relevance`` overrides the answer cut-off for calibration sweeps only (D-08).

        Production use keeps the provisional PRD medium threshold (the default).
        """
        self._corpus = corpus
        self._index = LexicalIndex(corpus)
        default = PROVISIONAL_BAND_THRESHOLDS["medium"]
        self._min_relevance = default if min_relevance is None else float(min_relevance)
        if not 0.0 < self._min_relevance <= 1.0:
            raise ValueError("min_relevance must be in (0, 1]")
        self._override = () if self._min_relevance == default else (f"min_relevance={self._min_relevance:.4f}",)

    @property
    def source_set_version(self) -> str:
        return self._corpus.source_set_version

    def run(
        self,
        context: RunContext,
        triage: TriageHandoff,
        *,
        acknowledged: Set[str],
        as_of: date,
        now: datetime | None = None,
    ) -> KnowledgeResult:
        created_at = utc_now(now)
        contribution_id = stable_id(
            "KNW",
            context.run_id,
            context.case_id,
            context.case_version,
            context.policy_version,
            triage.contribution_id,
            # Item-scoped runs only, so single-case IDs keep their form (K-2).
            *((triage.item_scope.identity.item_id,) if triage.item_scope is not None else ()),
            self._corpus.source_set_version,
            as_of.isoformat(),
            AGENT_VERSION,
            *self._override,
        )
        base = {
            "contribution_id": contribution_id,
            "agent": AGENT_NAME,
            "agent_version": AGENT_VERSION,
            "context": context,
            "input_refs": (triage.as_input_ref(),),
            "created_at": created_at,
            "source_set_version": self._corpus.source_set_version,
            "item_scope_ref": triage.item_scope.identity if triage.item_scope is not None else None,
        }

        gate = unique(
            [
                *upstream_reasons(context, [triage], acknowledged, must_be_completed=[triage]),
                *item_scope_reasons(context, triage),
            ]
        )
        if gate:
            return KnowledgeResult(
                **base,
                status=AgentStatus.BLOCKED,
                checkpoint=CheckpointOutcome(checkpoint="A3", passed=False, reason_codes=gate),
                claims=(
                    Claim(
                        statement="Retrieval did not run because the triage handoff was not usable.",
                        label=ClaimLabel.UNKNOWN,
                        confidence=ConfidenceBand.LOW,
                    ),
                ),
                confidence=ConfidenceBand.LOW,
                confidence_rationale="No retrieval was attempted.",
                unknowns=("Approved guidance for this case is unknown.",),
            )

        # The query is the (item) text only. Category, urgency, attention, Auditor
        # state, and item metadata never filter or reorder retrieval (K-3).
        query = triage.case_summary
        scored = self._index.search(query)
        min_terms = min(MIN_MATCHED_TERMS, max(1, self._index.query_term_count(query)))
        candidates = [
            s
            for s in scored
            if s.coverage >= self._min_relevance and len(s.matched_terms) >= min_terms
        ]

        eligible: list[ScoredSection] = []
        excluded: list[ExcludedSource] = []
        for candidate in candidates:
            reason = ineligibility_reason(candidate.article, as_of)
            if reason is None:
                eligible.append(candidate)
            else:
                excluded.append(
                    ExcludedSource(
                        doc_id=candidate.article.doc_id,
                        version=candidate.article.version,
                        section_id=candidate.section.section_id,
                        reason=reason,
                    )
                )

        unknowns: list[str] = [_UNCALIBRATED]
        if triage.product_area:
            in_area = [s for s in eligible if s.article.product_area == triage.product_area]
            if in_area:
                eligible = in_area
            elif eligible:
                unknowns.append(
                    f"Best approved evidence is outside the triage product area '{triage.product_area}'."
                )

        matched_terms = tuple(sorted({t for s in candidates for t in s.matched_terms}))
        base["matched_query_terms"] = matched_terms
        base["excluded_sources"] = tuple(excluded)

        if not eligible:
            if excluded:
                reason = (
                    ReasonCode.STALE_SOURCE_ONLY
                    if any(item.reason in _STALE_REASONS for item in excluded)
                    else ReasonCode.UNAPPROVED_SOURCE_ONLY
                )
            elif scored:
                reason = ReasonCode.WEAK_EVIDENCE
            else:
                reason = ReasonCode.NO_RELEVANT_SOURCE
            return self._abstain(base, (reason,), unknowns)

        # Ineligible-anchor guard (L-2): when the request's most specific word is not in the
        # best eligible section but is in an ineligible one, the on-topic source cannot be
        # used, so a current answer from another topic is withheld.
        anchor = self._index.anchor_term(query)
        if anchor is not None and anchor not in eligible[0].matched_terms:
            shadow = [s for s in scored if anchor in s.matched_terms and ineligibility_reason(s.article, as_of)]
            if shadow:
                known = {(item.doc_id, item.version, item.section_id) for item in excluded}
                shadow_excluded = []
                for item in shadow:
                    key = (item.article.doc_id, item.article.version, item.section.section_id)
                    if key not in known:
                        known.add(key)
                        shadow_excluded.append(
                            ExcludedSource(
                                doc_id=item.article.doc_id,
                                version=item.article.version,
                                section_id=item.section.section_id,
                                reason=ineligibility_reason(item.article, as_of),
                            )
                        )
                all_excluded = tuple(excluded) + tuple(shadow_excluded)
                base["excluded_sources"] = all_excluded
                reason = (
                    ReasonCode.STALE_SOURCE_ONLY
                    if any(item.reason in _STALE_REASONS for item in all_excluded)
                    else ReasonCode.UNAPPROVED_SOURCE_ONLY
                )
                unknowns.append(
                    "The request's most specific term matches only an ineligible source; "
                    "an answer from another topic is withheld."
                )
                return self._abstain(base, (reason,), unknowns)

        selected = eligible[:MAX_PASSAGES]

        flags: list[InjectionFlag] = []
        for item in selected:
            section = item.section
            texts = [section.heading, section.text]
            texts += [step.text for step in section.steps]
            texts += [entry.prompt for entry in section.information_needed]
            texts += [cond.text for cond in section.stop_conditions]
            for pattern_id in scan_for_injection(*texts):
                flags.append(
                    InjectionFlag(
                        doc_id=item.article.doc_id,
                        version=item.article.version,
                        section_id=section.section_id,
                        pattern_id=pattern_id,
                    )
                )
        if flags:
            flagged = {(f.doc_id, f.version, f.section_id) for f in flags}
            base["excluded_sources"] = tuple(excluded) + tuple(
                ExcludedSource(doc_id=d, version=v, section_id=s, reason=ReasonCode.RETRIEVED_INJECTION)
                for d, v, s in sorted(flagged)
            )
            base["injection_flags"] = tuple(flags)
            unknowns.append("A retrieved source contains instruction-like text; a human must review it.")
            return self._abstain(base, (ReasonCode.RETRIEVED_INJECTION,), unknowns)

        conflicts = self._conflicts(selected, as_of)
        if conflicts:
            base["conflicts"] = conflicts
            reasons = unique(conflict.reason for conflict in conflicts)
            claims = tuple(
                Claim(
                    statement=(
                        f"Approved sources {', '.join(ref.cite() for ref in conflict.sources)} "
                        f"both cover topic '{conflict.topic}'; the agent does not choose between them."
                    ),
                    label=ClaimLabel.VERIFIED,
                    sources=conflict.sources,
                    confidence=ConfidenceBand.HIGH,
                )
                for conflict in conflicts
            )
            unknowns.append("Which approved source is correct for this case is unresolved.")
            return self._abstain(base, reasons, unknowns, extra_claims=claims)

        passages = tuple(
            self._passage(item, rank) for rank, item in enumerate(selected, start=1)
        )
        top_band = passages[0].relevance_band
        if top_band is ConfidenceBand.MEDIUM:
            unknowns.append("Relevance is tentative (medium band); staff should confirm the guidance fits.")

        claims: list[Claim] = []
        for passage in passages:
            claims.append(
                Claim(
                    statement=(
                        f"{passage.source.cite()} is an approved source, effective "
                        f"{passage.effective_date.isoformat()}, review due {passage.review_due.isoformat()}."
                    ),
                    label=ClaimLabel.VERIFIED,
                    sources=(passage.source,),
                    confidence=ConfidenceBand.HIGH,
                )
            )
            claims.append(
                Claim(
                    statement=(
                        f"{passage.source.cite()} is relevant to the case query "
                        f"(term coverage {passage.relevance:.2f})."
                    ),
                    label=ClaimLabel.INFERENCE,
                    sources=(passage.source,),
                    basis="Lexical query-term coverage against approved sources; not human-verified.",
                    confidence=passage.relevance_band,
                )
            )

        return KnowledgeResult(
            **base,
            status=AgentStatus.COMPLETED,
            checkpoint=CheckpointOutcome(checkpoint="A3", passed=True),
            passages=passages,
            claims=tuple(claims),
            confidence=top_band,
            confidence_rationale=(
                f"Band of the top passage's query-term coverage ({passages[0].relevance:.2f}); "
                "provisional and uncalibrated."
            ),
            unknowns=tuple(unknowns),
        )

    def _conflicts(self, selected: list[ScoredSection], as_of: date) -> tuple[SourceConflict, ...]:
        conflicts: list[SourceConflict] = []
        seen_topics: set[str] = set()
        versions_by_doc = self._corpus.approved_versions_by_doc(as_of)
        eligible_articles = self._corpus.eligible_articles(as_of)
        for item in selected:
            article = item.article
            versions = versions_by_doc.get(article.doc_id, ())
            if len(versions) > 1:
                conflicts.append(
                    SourceConflict(
                        topic=article.topic,
                        reason=ReasonCode.MULTIPLE_APPROVED_VERSIONS,
                        sources=tuple(
                            kb_section_ref(v, item.section.section_id) for v in versions
                        ),
                    )
                )
            if article.topic in seen_topics:
                continue
            seen_topics.add(article.topic)
            same_topic = [
                other
                for other in eligible_articles
                if other.topic == article.topic and other.doc_id != article.doc_id
            ]
            if same_topic:
                refs = [kb_section_ref(article, item.section.section_id)]
                refs += [
                    SourceRef(kind=SourceKind.KB_SECTION, source_id=o.doc_id, version=o.version)
                    for o in same_topic
                ]
                conflicts.append(
                    SourceConflict(
                        topic=article.topic,
                        reason=ReasonCode.CONFLICTING_SOURCES,
                        sources=tuple(refs),
                    )
                )
        return tuple(conflicts)

    @staticmethod
    def _passage(item: ScoredSection, rank: int) -> EvidencePassage:
        article, section = item.article, item.section
        return EvidencePassage(
            source=kb_section_ref(article, section.section_id),
            doc_id=article.doc_id,
            version=article.version,
            section_id=section.section_id,
            title=article.title,
            heading=section.heading,
            topic=article.topic,
            product_area=article.product_area,
            text=section.text,
            steps=tuple(
                PassageStep(step_id=s.step_id, action_type=s.action_type, text=s.text)
                for s in section.steps
            ),
            information_needed=tuple(
                PassageInformationItem(field=i.field, prompt=i.prompt)
                for i in section.information_needed
            ),
            stop_conditions=tuple(
                PassageStopCondition(condition_id=c.condition_id, text=c.text)
                for c in section.stop_conditions
            ),
            effective_date=article.effective_date,
            review_due=article.review_due,
            relevance=item.coverage,
            relevance_band=band_for(item.coverage),
            rank=rank,
        )

    @staticmethod
    def _abstain(
        base: dict,
        reasons: tuple[ReasonCode, ...],
        unknowns: list[str],
        *,
        extra_claims: tuple[Claim, ...] = (),
    ) -> KnowledgeResult:
        claim = Claim(
            statement=(
                "No approved, current, non-conflicting source supports product guidance for this "
                f"case ({', '.join(reasons)})."
            ),
            label=ClaimLabel.UNKNOWN,
            confidence=ConfidenceBand.LOW,
        )
        return KnowledgeResult(
            **base,
            status=AgentStatus.ABSTAINED,
            checkpoint=CheckpointOutcome(checkpoint="A3", passed=False, reason_codes=reasons),
            claims=(claim, *extra_claims),
            confidence=ConfidenceBand.LOW,
            confidence_rationale="Abstained: evidence is missing, weak, stale, conflicting, or unsafe.",
            unknowns=tuple(unknowns),
        )
