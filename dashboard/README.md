# DHLCO2 Interactive Dashboard

Local Streamlit demo app. Shows the deterministic decision model's output for a
chosen scenario — not real DHL telemetry (KPI catalog status remains `candidate`
until the pilot scope is resolved, see `NEXT_STEPS.md`).

## Run it

```powershell
uv sync --extra dashboard
uv run streamlit run dashboard/app.py
```

Opens at `http://localhost:8501` in the default browser. No deployment/hosting
needed — designed to run on the presenter's own laptop during a meeting.

## Tabs

1. **KPI-Katalog & Green Gates** — all 19 KPIs, status, whether a Green Gate is defined
2. **Hardware-Vergleich** — EfficiencyScore / CO2 / EUR per hardware tier for the sidebar scenario
3. **Pareto-Frontier** — CO2 vs. cost vs. EfficiencyScore, highlights the Pareto-optimal subset
4. **Sensitivität** — CO2/request vs. request volume, and grid vs. PV 70% comparison
5. **Live-Kontext** — live German grid carbon intensity (energy-charts.info) + Boavizta embodied-carbon references
6. **Auditability** — evidence ledger of simulation runs (RUN-ID, git commit, output hashes)

## Files

- `app.py` — Streamlit UI (thin, calls `data_helpers.py`)
- `data_helpers.py` — pure data-shaping functions, no Streamlit import, unit-tested in `tests/test_dashboard_helpers.py`
- Smoke-tested end-to-end via Streamlit's `AppTest` harness in `tests/test_dashboard_app.py`
