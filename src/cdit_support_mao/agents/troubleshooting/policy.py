"""Versioned Tier 1 troubleshooting boundary used by the Troubleshooting agent.

The policy lists which guidance action types a Tier 1 specialist may suggest,
which are reserved for authorized staff, and which are forbidden. Request and
stop-condition patterns are deterministic risk signals over untrusted case
text; a match can only restrict what the agent suggests, never grant authority.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Literal

from pydantic import Field, ValidationError, field_validator, model_validator

from cdit_support_mao.contracts.common import StrictModel

POLICY_PATH_ENV = "CDIT_TROUBLESHOOTING_POLICY"
# 0.1.2 adds the privilege-escalation pattern to RR-06. 0.1.1 stays in place for callers that
# still name it (the shared and Manny harnesses, and the evaluation draft's citations).
DEFAULT_POLICY_PATH = Path("synthetic_data/policy/troubleshooting-policy_v0.1.2.json")

# Quoted spans in untrusted case text. Straight and curly single quotes allow an
# apostrophe inside a word (can't, site's) and must not start or end inside a word.
_QUOTE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r'"([^"\n]+)"'),
    re.compile(r"“([^”\n]+)”"),
    re.compile(r"(?<!\w)'((?:[^'\n]|'(?=\w))+)'(?!\w)"),
    re.compile(r"(?<!\w)‘((?:[^’\n]|’(?=\w))+)’(?!\w)"),
)

RuleMatch = Literal["none", "direct", "quoted"]


def quoted_spans(text: str) -> tuple[tuple[int, int], ...]:
    """Return (start, end) offsets of the content of each quoted span in ``text``."""
    return tuple(sorted(match.span(1) for pattern in _QUOTE_PATTERNS for match in pattern.finditer(text)))


class PolicyError(ValueError):
    """The troubleshooting policy is missing or invalid; the agent must not run."""


def _compiles(pattern: str) -> str:
    try:
        re.compile(pattern, re.IGNORECASE)
    except re.error as error:
        raise ValueError(f"invalid pattern: {error}") from error
    return pattern


class RestrictedRequestRule(StrictModel):
    rule_id: str = Field(pattern=r"^RR-[0-9]{2}$")
    action_type: str
    effect: Literal["block", "flag"]
    signal: str
    # "signal_only": a match that lies entirely inside quotation marks is quoted case
    # data (for example a training example), so it raises a signal instead of the
    # rule's effect. Any match outside quotes still applies the effect.
    quoted_match: Literal["apply", "signal_only"] = "apply"
    pattern: str

    @field_validator("pattern")
    @classmethod
    def _check_pattern(cls, value: str) -> str:
        return _compiles(value)

    def matches(self, text: str) -> bool:
        return re.search(self.pattern, text, re.IGNORECASE) is not None

    def evaluate(self, text: str) -> RuleMatch:
        """Classify the rule's matches in ``text``.

        ``quoted`` only when the rule opts in and every match lies inside one quoted
        span. A match that crosses a quote boundary counts as ``direct``, so ambiguity
        keeps the stricter effect.
        """
        found = [match.span() for match in re.finditer(self.pattern, text, re.IGNORECASE)]
        if not found:
            return "none"
        if self.quoted_match == "apply":
            return "direct"
        spans = quoted_spans(text)
        inside = all(any(start <= m_start and m_end <= end for start, end in spans) for m_start, m_end in found)
        return "quoted" if inside else "direct"


class GlobalStopCondition(StrictModel):
    condition_id: str = Field(pattern=r"^TS-SC-[A-Z]+$")
    signal: str
    halts_routine_steps: bool
    text: str
    pattern: str

    @field_validator("pattern")
    @classmethod
    def _check_pattern(cls, value: str) -> str:
        return _compiles(value)

    def matches(self, text: str) -> bool:
        return re.search(self.pattern, text, re.IGNORECASE) is not None


class TroubleshootingPolicy(StrictModel):
    policy_id: str
    version: str
    status: Literal["proposed", "approved"]
    data_classification: Literal["synthetic"]
    description: str
    tier1_action_types: dict[str, Literal["tier1_guides_customer", "tier1_specialist"]]
    staff_only_action_types: tuple[str, ...]
    forbidden_action_types: tuple[str, ...]
    restricted_request_rules: tuple[RestrictedRequestRule, ...]
    global_stop_conditions: tuple[GlobalStopCondition, ...]

    @model_validator(mode="after")
    def _disjoint_action_types(self) -> TroubleshootingPolicy:
        tier1 = set(self.tier1_action_types)
        staff = set(self.staff_only_action_types)
        forbidden = set(self.forbidden_action_types)
        if tier1 & staff or tier1 & forbidden or staff & forbidden:
            raise ValueError("tier1, staff-only, and forbidden action types must not overlap")
        return self

    def classify(self, action_type: str) -> Literal["tier1", "staff_only", "forbidden", "unknown"]:
        if action_type in self.forbidden_action_types:
            return "forbidden"
        if action_type in self.staff_only_action_types:
            return "staff_only"
        if action_type in self.tier1_action_types:
            return "tier1"
        return "unknown"


def default_policy_path() -> Path:
    return Path(os.environ.get(POLICY_PATH_ENV, str(DEFAULT_POLICY_PATH))).expanduser()


def load_policy(path: Path | None = None) -> TroubleshootingPolicy:
    path = path or default_policy_path()
    try:
        return TroubleshootingPolicy.model_validate(json.loads(path.read_text(encoding="utf-8")))
    except FileNotFoundError as error:
        raise PolicyError(f"troubleshooting policy not found: {path}") from error
    except (json.JSONDecodeError, ValidationError) as error:
        raise PolicyError(f"invalid troubleshooting policy {path}: {error}") from error
