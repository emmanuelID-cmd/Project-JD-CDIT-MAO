"""Detect PHI-like or credential-like strings before a draft note is released.

Patterns target synthetic test strings (PRD "Protect sensitive data" metric).
They are a backstop, not a de-identification method: real PHI must never reach
this prototype. Findings record only the category and location; the matched
value is never stored, logged, or echoed.
"""

from __future__ import annotations

import re

PRIVACY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (category, re.compile(pattern, re.IGNORECASE))
    for category, pattern in (
        ("ssn_like", r"\b\d{3}-\d{2}-\d{4}\b"),
        (
            "date_of_birth",
            r"\b(dob|date of birth|birth ?date|born on)\b\W{0,3}\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}",
        ),
        ("medical_record_number", r"\b(mrn|medical record( number)?)\b\W{0,3}[a-z0-9-]{4,}"),
        ("email_address", r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b"),
        ("phone_number", r"(?<![\w-])(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?![\w-])"),
        # A value must look secret-like (contains a digit or symbol) so headings such as
        # "Forgotten password: self-service reset" are not flagged.
        (
            "credential",
            r"\b(password|passwd|pwd|api[_ -]?key|secret|token)\s*[:=]\s*(?=\S*[0-9!@#$%^&*_+=])\S{6,}",
        ),
        ("patient_identifier", r"\b(patient|subject)\s+(name|id|identifier|number)\b\W{0,3}\w+"),
    )
)


def scan_for_sensitive_data(text: str) -> tuple[str, ...]:
    """Return the sorted, unique categories of sensitive-looking data in ``text``."""
    return tuple(sorted({category for category, pattern in PRIVACY_PATTERNS if pattern.search(text)}))
