# Local Grafana Demo

This is the Grafana-first Phase A path to a first RCA report.

It runs a bundled Grafana-style alert and bundled Loki, Mimir, and alert-rule evidence locally, then renders the RCA in your terminal.

## Prerequisites

- Python 3.11+
- `make`
- `ANTHROPIC_API_KEY` in `.env` or your shell

If you prefer OpenAI instead:

```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key
```

## Run the demo

```bash
make install
cp .env.example .env
# add ANTHROPIC_API_KEY to .env
make local-grafana-demo
```

## What this gives you

- A Grafana alert payload
- Bundled Grafana logs that show the failure mechanism
- Bundled metrics that show the freshness symptom
- Bundled alert rule metadata for RCA context
- A rendered RCA report using the real diagnosis and report pipeline

## Save the report to a file

```bash
python3 -m app.demo.local_grafana_rca --output /tmp/tracer-local-grafana-rca.md
```

## Notes

This is the lowest-friction Grafana example. It does not require a live Grafana instance or real Grafana credentials.

For the generic local RCA example, see [local-rca-demo.md](local-rca-demo.md).

For a live local Grafana stack instead of bundled evidence, see [local-grafana-live.md](local-grafana-live.md).

For the full local development flow, see [SETUP.md](../SETUP.md).
