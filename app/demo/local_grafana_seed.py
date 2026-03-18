"""Seed a local Grafana+Loki demo stack with sample failure logs."""

from __future__ import annotations

import json
import time

import requests

LOCAL_LOKI_URL = "http://localhost:3100"
SERVICE_NAME = "prefect-etl-pipeline-local"
PIPELINE_NAME = "events_fact"


def wait_for_loki(timeout_seconds: int = 30) -> None:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            response = requests.get(f"{LOCAL_LOKI_URL}/ready", timeout=2)
            if response.status_code == 200:
                return
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(1)
    raise SystemExit(
        "Local Loki is not ready. Start the stack with `make grafana-local-up` "
        f"and retry. Last error: {last_error}"
    )


def build_log_stream(now_ns: int) -> dict:
    base_labels = {
        "service_name": SERVICE_NAME,
        "pipeline_name": PIPELINE_NAME,
        "environment": "local",
    }
    values = [
        [str(now_ns - 8_000_000_000), "prefect-etl-pipeline-local starting scheduled run for events_fact"],
        [str(now_ns - 6_000_000_000), "extract_events_fact requesting Snowflake credentials from configured secret"],
        [
            str(now_ns - 4_000_000_000),
            "snowflake.connector.errors.DatabaseError: 250001 (08001): Failed to connect to DB: JWT token is invalid or expired",
        ],
        [
            str(now_ns - 2_000_000_000),
            "events_fact pipeline aborted before the load step because Snowflake authentication failed",
        ],
    ]
    return {"stream": base_labels, "values": values}


def seed_logs() -> None:
    wait_for_loki()
    payload = {"streams": [build_log_stream(time.time_ns())]}
    response = requests.post(
        f"{LOCAL_LOKI_URL}/loki/api/v1/push",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        timeout=5,
    )
    response.raise_for_status()


def main() -> int:
    seed_logs()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
