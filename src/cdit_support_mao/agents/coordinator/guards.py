"""Manny-owned A0/A1 risk signals for synthetic input, not a trust decision."""
from __future__ import annotations

import re

_INSTRUCTION_PATTERNS = (
    ("override_instruction", re.compile(r"\b(?:ignore|disregard|forget)\s+(?:all\s+|your\s+|the\s+|previous\s+|prior\s+)*(?:instructions|rules|policies|policy)\b", re.I)),
    ("role_spoof", re.compile(r"\b(?:you are now|act as)\s+(?:an?\s+)?(?:administrator|admin|system)\b", re.I)),
    ("prompt_or_secret_request", re.compile(r"\b(?:reveal|print|send|expose)\s+(?:the\s+)?(?:system prompt|credentials|secrets|api keys)\b", re.I)),
    ("speaker_delimiter", re.compile(r"(?:^|\n)\s*(?:system|assistant|developer)\s*:", re.I)),
    ("hidden_format_control", re.compile("[\u200b\u202a-\u202e\u2066-\u2069\x00-\x08\x0b\x0c\x0e-\x1f]")),
)
_PRIVACY_PATTERNS = (
    ("email_like", re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", re.I)),
    ("ssn_like", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("credential_like", re.compile(r"\b(?:password|api[_ -]?key|token|secret)\s*[:=]\s*\S{6,}", re.I)),
    ("patient_identifier", re.compile(r"\b(?:patient|subject)\s+(?:id|identifier|number|name)\b\W{0,3}\w+", re.I)),
    ("date_of_birth", re.compile(r"\b(?:dob|date of birth)\b\W{0,3}\d{1,4}[-/.]\d{1,2}[-/.]\d{1,4}", re.I)),
    ("medical_record_number", re.compile(r"\b(?:mrn|medical record number)\b\W{0,3}[a-z0-9-]{4,}", re.I)),
    ("phone_like", re.compile(r"(?<![\w-])(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?![\w-])")),
)

def scan_for_injection(text: str) -> tuple[str, ...]:
    return tuple(name for name, pattern in _INSTRUCTION_PATTERNS if pattern.search(text))

def scan_for_sensitive_data(text: str) -> tuple[str, ...]:
    return tuple(name for name, pattern in _PRIVACY_PATTERNS if pattern.search(text))
