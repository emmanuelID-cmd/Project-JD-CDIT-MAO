"""Conservative, source-preserving segmentation of synthetic case text.

No category, urgency, route, model call, or external ticket action occurs here.
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from pydantic import Field

from cdit_support_mao.agents.coordinator.handoff import HandoffRegistry
from cdit_support_mao.agents.triage.input import read_acknowledged_input
from cdit_support_mao.contracts.common import RunContext, SourceRef, StrictModel


class RequestItem(StrictModel):
    item_index: int = Field(strict=True, ge=1, le=8)
    reported_text: str = Field(min_length=1, max_length=2000, repr=False)
    start_codepoint: int = Field(strict=True, ge=0)
    end_codepoint: int = Field(strict=True, ge=1)
    source: SourceRef
    trust: Literal["untrusted_case_data"] = "untrusted_case_data"
    classification: Literal["unclassified"] = "unclassified"


class SegmentationResult(StrictModel):
    trace_id: str
    handoff_id: str
    context: RunContext
    items: tuple[RequestItem, ...] = Field(min_length=1, max_length=8)
    status: Literal["segmented_needs_classification", "needs_auditor"]
    reason_code: Literal["segmented", "uncertain_segmentation", "too_many_items"]
    human_review_required: Literal[True] = True


_CONJUNCTION = re.compile(r"\s+(?:and|also)\s+(?=(?:i|we|my|our)\b)", re.I)
_UNCERTAIN_CONJUNCTION = re.compile(r"\s+(?:and|also)\b", re.I)


def _parts(text: str) -> tuple[list[tuple[int, int]], str]:
    """Find explicit separators without splitting quoted text or contractions."""
    spans: list[tuple[int, int]] = []
    start = index = 0
    quote: str | None = None
    uncertain = False
    while index < len(text):
        char = text[index]
        previous = text[index - 1] if index else ""
        following = text[index + 1] if index + 1 < len(text) else ""
        apostrophe = char in ("'", "’") and previous.isalnum() and following.isalnum()
        quote_pairs = {"'": "'", '"': '"', "‘": "’", "“": "”"}
        backslashes = 0
        back = index - 1
        while back >= 0 and text[back] == "\\":
            backslashes += 1
            back -= 1
        escaped = backslashes % 2 == 1
        if quote is not None and char == quote and not escaped:
            quote = None
            index += 1
            continue
        if quote is None and char in ("’", "”") and not apostrophe:
            uncertain = True
            index += 1
            continue
        if quote is None and escaped and char in quote_pairs:
            uncertain = True
            index += 1
            continue
        if quote is None and char in quote_pairs and not apostrophe and not escaped:
            quote = quote_pairs[char]
            index += 1
            continue
        if quote is None:
            match = _CONJUNCTION.match(text, index)
            if not match and _UNCERTAIN_CONJUNCTION.match(text, index):
                uncertain = True
            if char in ";\n" or match:
                end = index
                while start < end and text[start].isspace():
                    start += 1
                while end > start and text[end - 1].isspace():
                    end -= 1
                if end > start:
                    spans.append((start, end))
                index = match.end() if match else index + 1
                start = index
                continue
        index += 1
    end = len(text)
    while start < end and text[start].isspace():
        start += 1
    while end > start and text[end - 1].isspace():
        end -= 1
    if end > start:
        spans.append((start, end))
    if not spans or quote is not None or uncertain:
        return [(0, len(text))], "uncertain_segmentation"
    if len(spans) > 8:
        return [(0, len(text))], "too_many_items"
    return spans, "segmented"


def extract_request_parts(registry: HandoffRegistry, *, handoff_id: str,
                          expected_version: int, receiver_capability: object,
                          context: RunContext, now: datetime | None = None) -> SegmentationResult:
    """Revalidate the handoff and return bounded, exact-source request spans."""
    packet = read_acknowledged_input(registry, handoff_id=handoff_id,
        expected_version=expected_version, receiver_capability=receiver_capability, context=context, now=now)
    spans, reason = _parts(packet.reported_message)
    items = tuple(RequestItem(item_index=index, reported_text=packet.reported_message[start:end],
        start_codepoint=start, end_codepoint=end, source=packet.source)
        for index, (start, end) in enumerate(spans, 1))
    return SegmentationResult(trace_id=packet.trace_id, handoff_id=packet.handoff_id,
        context=packet.context, items=items,
        status="segmented_needs_classification" if reason == "segmented" else "needs_auditor",
        reason_code=reason)
