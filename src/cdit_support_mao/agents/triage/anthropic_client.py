"""Create an Anthropic client from the project-local ignored .env file.

Client construction does not send a request. Callers still need the adapter's
explicit per-run authorization and current-handoff preflight to make a request.
"""
from __future__ import annotations

import os
from pathlib import Path

from anthropic import Anthropic
from dotenv import dotenv_values

from cdit_support_mao.agents.triage.anthropic_adapter import (
    MODEL_ID,
    REQUEST_TIMEOUT_SECONDS,
)


PROJECT_ROOT = Path(__file__).resolve().parents[4]


class AnthropicClientConfigurationError(ValueError):
    """Content-free failure for missing or inconsistent local API settings."""


def create_anthropic_client(*, env_file: Path | None = None) -> Anthropic:
    """Read deployment environment or local .env without making a request."""
    path = env_file or PROJECT_ROOT / ".env"
    uses_process_environment = env_file is None
    environment_key = os.environ.get("ANTHROPIC_API_KEY") if uses_process_environment else None
    if not path.is_file() and not environment_key:
        raise AnthropicClientConfigurationError("anthropic_env_file_missing")

    values = dotenv_values(path) if path.is_file() else {}
    model_id = (
        os.environ.get("CDIT_TRIAGE_MODEL") if uses_process_environment else None
    ) or values.get("CDIT_TRIAGE_MODEL", MODEL_ID)
    if model_id != MODEL_ID:
        raise AnthropicClientConfigurationError("anthropic_model_id_mismatch")
    api_key = environment_key or values.get("ANTHROPIC_API_KEY")
    if not isinstance(api_key, str) or not api_key.strip():
        raise AnthropicClientConfigurationError("anthropic_api_key_missing")

    return Anthropic(
        api_key=api_key.strip(),
        max_retries=0,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
