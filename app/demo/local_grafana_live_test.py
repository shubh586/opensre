from __future__ import annotations

from app.demo.local_grafana_live import LOCAL_GRAFANA_URL, build_synthetic_alert, prepare_demo_state


def test_build_synthetic_alert_points_to_local_grafana() -> None:
    alert = build_synthetic_alert()

    assert alert["externalURL"] == LOCAL_GRAFANA_URL
    assert alert["commonLabels"]["pipeline_name"] == "events_fact"


def test_prepare_demo_state_sets_live_grafana_endpoint() -> None:
    evidence = {
        "grafana_logs": [{"message": "demo log"}],
        "grafana_error_logs": [{"message": "demo error"}],
        "grafana_logs_query": '{service_name="prefect-etl-pipeline-local"}',
        "grafana_logs_service": "prefect-etl-pipeline-local",
    }

    state = prepare_demo_state(evidence)

    assert state["alert_source"] == "grafana"
    assert state["available_sources"]["grafana"]["grafana_endpoint"] == LOCAL_GRAFANA_URL
    assert state["evidence"]["grafana_logs_service"] == "prefect-etl-pipeline-local"
