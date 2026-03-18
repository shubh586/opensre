from __future__ import annotations

from app.agent.tools.clients.grafana.config import GrafanaAccountConfig


def test_is_configured_with_read_token() -> None:
    config = GrafanaAccountConfig(
        account_id="test",
        instance_url="https://example.grafana.net",
        read_token="secret",
    )

    assert config.is_configured is True


def test_is_configured_for_local_anonymous_grafana() -> None:
    config = GrafanaAccountConfig(
        account_id="local",
        instance_url="http://localhost:3000",
        read_token="",
    )

    assert config.is_configured is True
