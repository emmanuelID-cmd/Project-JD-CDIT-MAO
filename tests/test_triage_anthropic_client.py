from __future__ import annotations

from pathlib import Path

import pytest

from cdit_support_mao.agents.triage.anthropic_client import (
    AnthropicClientConfigurationError,
    create_anthropic_client,
)


def test_client_factory_requires_an_env_file(tmp_path: Path):
    with pytest.raises(AnthropicClientConfigurationError, match="env_file_missing"):
        create_anthropic_client(env_file=tmp_path / ".env")


def test_client_factory_fails_closed_when_key_is_blank(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("CDIT_TRIAGE_MODEL=claude-sonnet-5-5\nANTHROPIC_API_KEY=\n", encoding="utf-8")
    with pytest.raises(AnthropicClientConfigurationError, match="api_key_missing"):
        create_anthropic_client(env_file=env_file)


def test_client_factory_rejects_a_different_model_alias(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("CDIT_TRIAGE_MODEL=other-model\nANTHROPIC_API_KEY=test-only-key\n", encoding="utf-8")
    with pytest.raises(AnthropicClientConfigurationError, match="model_id_mismatch"):
        create_anthropic_client(env_file=env_file)


def test_client_factory_constructs_without_calling_provider(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CDIT_TRIAGE_MODEL=claude-sonnet-5-5\nANTHROPIC_API_KEY=test-only-key\n",
        encoding="utf-8",
    )
    client = create_anthropic_client(env_file=env_file)

    assert client.api_key == "test-only-key"
    assert client.max_retries == 0
