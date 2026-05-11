"""Tests for Bedrock-specific model validation and custom ID handling."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from app.cli.interactive_shell.command_registry.model import (
    _is_model_supported,
    _prompt_custom_model_id,
    _reasoning_model_menu_choices,
    _toolcall_model_menu_choices,
)


@dataclass(frozen=True)
class _FakeModelOption:
    value: str
    label: str = ""


@dataclass(frozen=True)
class _FakeProvider:
    value: str
    models: tuple[_FakeModelOption, ...] = ()


# ─────────────────────────────────────────────────────────────────────────────
# _is_model_supported — Bedrock bypass
# ─────────────────────────────────────────────────────────────────────────────


class TestIsModelSupportedBedrock:
    """Bedrock must accept any non-empty model string (ARNs, regional prefixes, etc.)."""

    def test_bedrock_accepts_inference_profile_id(self) -> None:
        assert _is_model_supported("bedrock", "us.anthropic.claude-sonnet-4-6", ()) is True

    def test_bedrock_accepts_eu_prefix(self) -> None:
        assert _is_model_supported("bedrock", "eu.anthropic.claude-sonnet-4-6", ()) is True

    def test_bedrock_accepts_global_prefix(self) -> None:
        assert _is_model_supported("bedrock", "global.anthropic.claude-opus-4-7", ()) is True

    def test_bedrock_accepts_on_demand_model(self) -> None:
        assert _is_model_supported("bedrock", "mistral.mistral-large-3-675b-instruct", ()) is True

    def test_bedrock_accepts_full_arn(self) -> None:
        arn = "arn:aws:bedrock:us-east-1:123456789012:inference-profile/my-profile"
        assert _is_model_supported("bedrock", arn, ()) is True

    def test_bedrock_rejects_empty_string(self) -> None:
        assert _is_model_supported("bedrock", "", ()) is False

    def test_ollama_also_accepts_any_model(self) -> None:
        """Ollama shares the same bypass pattern — verify it still works."""
        assert _is_model_supported("ollama", "llama3.2", ()) is True

    def test_other_provider_requires_match(self) -> None:
        """Non-bypass providers must match the curated model list."""
        models = (_FakeModelOption(value="gpt-5.4"),)
        assert _is_model_supported("openai", "gpt-5.4", models) is True
        assert _is_model_supported("openai", "gpt-unknown", models) is False


# ─────────────────────────────────────────────────────────────────────────────
# Menu choices — __custom__ sentinel
# ─────────────────────────────────────────────────────────────────────────────


class TestMenuChoicesCustomOption:
    """Bedrock menus must include the __custom__ escape hatch."""

    def test_reasoning_menu_includes_custom_for_bedrock(self) -> None:
        provider = _FakeProvider(
            value="bedrock", models=(_FakeModelOption(value="us.anthropic.claude-sonnet-4-6"),)
        )
        choices = _reasoning_model_menu_choices(provider)
        values = [v for v, _ in choices]
        assert "__custom__" in values

    def test_toolcall_menu_includes_custom_for_bedrock(self) -> None:
        provider = _FakeProvider(
            value="bedrock", models=(_FakeModelOption(value="us.anthropic.claude-sonnet-4-6"),)
        )
        choices = _toolcall_model_menu_choices(provider)
        values = [v for v, _ in choices]
        assert "__custom__" in values

    def test_reasoning_menu_no_custom_for_openai(self) -> None:
        provider = _FakeProvider(value="openai", models=(_FakeModelOption(value="gpt-5.4"),))
        choices = _reasoning_model_menu_choices(provider)
        values = [v for v, _ in choices]
        assert "__custom__" not in values

    def test_toolcall_menu_no_custom_for_openai(self) -> None:
        provider = _FakeProvider(value="openai", models=(_FakeModelOption(value="gpt-5.4"),))
        choices = _toolcall_model_menu_choices(provider)
        values = [v for v, _ in choices]
        assert "__custom__" not in values


# ─────────────────────────────────────────────────────────────────────────────
# _prompt_custom_model_id
# ─────────────────────────────────────────────────────────────────────────────


class TestPromptCustomModelId:
    """Custom model ID prompt edge cases."""

    def test_returns_stripped_value(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from rich.console import Console

        console = Console(force_terminal=False)
        monkeypatch.setattr(console, "input", lambda _prompt: "  us.anthropic.claude-opus-4-7  ")
        result = _prompt_custom_model_id(console)
        assert result == "us.anthropic.claude-opus-4-7"

    def test_returns_none_on_empty_input(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from rich.console import Console

        console = Console(force_terminal=False)
        monkeypatch.setattr(console, "input", lambda _prompt: "   ")
        result = _prompt_custom_model_id(console)
        assert result is None

    def test_returns_none_on_keyboard_interrupt(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from rich.console import Console

        console = Console(force_terminal=False)

        def _raise_interrupt(_prompt: str) -> str:
            raise KeyboardInterrupt

        monkeypatch.setattr(console, "input", _raise_interrupt)
        result = _prompt_custom_model_id(console)
        assert result is None

    def test_returns_none_on_eof(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from rich.console import Console

        console = Console(force_terminal=False)

        def _raise_eof(_prompt: str) -> str:
            raise EOFError

        monkeypatch.setattr(console, "input", _raise_eof)
        result = _prompt_custom_model_id(console)
        assert result is None


# ─────────────────────────────────────────────────────────────────────────────
# Bedrock ProviderOption in wizard config
# ─────────────────────────────────────────────────────────────────────────────


class TestBedrockProviderConfig:
    """Verify Bedrock is registered correctly in the wizard config."""

    def test_bedrock_in_supported_providers(self) -> None:
        from app.cli.wizard.config import PROVIDER_BY_VALUE

        assert "bedrock" in PROVIDER_BY_VALUE

    def test_bedrock_credential_kind_is_none(self) -> None:
        from app.cli.wizard.config import PROVIDER_BY_VALUE

        provider = PROVIDER_BY_VALUE["bedrock"]
        assert provider.credential_kind == "none"

    def test_bedrock_has_curated_models(self) -> None:
        from app.cli.wizard.config import PROVIDER_BY_VALUE

        provider = PROVIDER_BY_VALUE["bedrock"]
        assert len(provider.models) >= 10

    def test_bedrock_curated_models_use_inference_profiles(self) -> None:
        """All Claude models in the curated list must use us.* inference profile IDs."""
        from app.cli.wizard.config import PROVIDER_BY_VALUE

        provider = PROVIDER_BY_VALUE["bedrock"]
        claude_models = [m for m in provider.models if "anthropic" in str(getattr(m, "value", ""))]
        for model in claude_models:
            value = str(getattr(model, "value", ""))
            assert value.startswith("us."), (
                f"Claude model '{value}' must use a us.* inference profile ID"
            )

    def test_bedrock_has_toolcall_model_env(self) -> None:
        from app.cli.wizard.config import PROVIDER_BY_VALUE

        provider = PROVIDER_BY_VALUE["bedrock"]
        assert provider.toolcall_model_env == "BEDROCK_TOOLCALL_MODEL"
