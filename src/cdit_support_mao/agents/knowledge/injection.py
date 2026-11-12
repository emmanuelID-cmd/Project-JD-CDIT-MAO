"""Detect instruction-like content inside retrieved knowledge passages.

Detection is a risk signal only (PRD A1/A3): retrieved text is always untrusted
evidence whether or not a pattern matches. The agents in this lane never
execute text as instructions; a match makes the Knowledge agent abstain so a
human reviews the source.
"""

from __future__ import annotations

import re

INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (pattern_id, re.compile(pattern, re.IGNORECASE))
    for pattern_id, pattern in (
        (
            "INJ-01-ignore-instructions",
            r"\b(ignore|disregard|forget)\s+(all\s+|any\s+|the\s+|your\s+|previous\s+|prior\s+|above\s+)*"
            r"(instructions|policy|policies|rules|guidelines|directions)\b",
        ),
        (
            "INJ-02-override-safeguards",
            r"\b(override|bypass|disable)\s+(the\s+|your\s+|all\s+|any\s+)*"
            r"(policy|policies|rules|safeguards|guardrails|restrictions)\b",
        ),
        ("INJ-03-prompt-reference", r"\b(system|developer)\s+(prompt|message|instructions)\b"),
        ("INJ-04-role-hijack", r"\byou\s+are\s+now\b|\bact\s+as\s+(an?\s+)?(admin|administrator|system)\b"),
        ("INJ-05-speaker-tag", r"(^|[.!?]\s+|\n)\s*(assistant|system|ai|model)\s*:"),
        (
            "INJ-06-secret-disclosure",
            r"\breveal\s+(the\s+|all\s+|any\s+)?(administrator\s+|admin\s+)?"
            r"(passwords?|credentials?|secrets?|api\s+keys?|tokens?)\b",
        ),
        (
            "INJ-07-exfiltration",
            r"\b(send|forward|email|post)\b[^.]{0,80}\b(to|at)\s+[\w.+-]+@[\w-]+\.[\w.]+",
        ),
    )
)


def scan_for_injection(*texts: str) -> tuple[str, ...]:
    """Return the ids of injection patterns found in any of ``texts`` (sorted, unique)."""
    found = {
        pattern_id
        for text in texts
        for pattern_id, pattern in INJECTION_PATTERNS
        if pattern.search(text)
    }
    return tuple(sorted(found))
