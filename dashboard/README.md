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

## Flow

The app leads with the decision question ("which infrastructure configuration is
best for this workload, under CO2/cost/efficiency?"), not the KPI catalog:

1. **Sidebar** — pick a named example scenario (`generators/demo_scenarios.py`,
   10 illustrative DHL-style workloads, see `docs/demo_scenario_matrix.md`) or
   "Custom / Freie Eingabe". Every Stellvariable underneath stays fully adjustable —
   the scenario only seeds sensible defaults.
2. **Result box** (always visible, independent of the open tab) — recommended
   config, CO2/request, cost/useful-outcome, aggregated Green-Gate status,
   data-quality note.
3. **Tabs**, in decision order:

| # | Tab | Content |
|---|---|---|
| 1 | **Entscheidung & Begründung** | Full rationale, Green-Gate breakdown per contributing KPI, ranked CO2/cost levers ("stärkster verbleibender Hebel" — remaining headroom from the scenario's current values, not a fixed-bounds spread), Pilotfähigkeit note |
| 2 | **Hardware-Vergleich** | EfficiencyScore / CO2 / EUR per hardware tier, incl. per-config aggregated Gate column |
| 3 | **Pareto-Frontier** | CO2 vs. cost vs. EfficiencyScore, highlights the Pareto-optimal subset |
| 4 | **Sensitivität (Detail)** | CO2/request vs. request volume, grid vs. PV 70% comparison (supplementary detail to the lever ranking in tab 1) |
| 5 | **KPI-Katalog & Green Gates** | All 19 KPIs, status, whether a Green Gate is defined |
| 6 | **Live-Kontext** | Live German/EU grid carbon intensity (energy-charts.info, ENTSO-E) + Boavizta embodied-carbon references — the same live sources are selectable directly in the sidebar's Netz-EF control, not just informational here |
| 7 | **Auditability** | Evidence ledger of simulation runs (RUN-ID, git commit, output hashes) |
| 8 | **Cross-Repo-Benchmark** | Real Eco-CI measurements across 7 repos, showing the methodology is technology-independent |

## Recommendation logic

`generators/decision_support.py` picks a Pareto-optimal, Green-Gate-compliant
configuration (tie-break: the model's own documented EfficiencyScore) rather than
inventing a new weighted "master score". If every feasible configuration is
Gate-red for a scenario, the recommendation still returns the least-critical
option but flags `all_candidates_red` — the dashboard surfaces this as an
explicit warning instead of quietly showing "the best of a bad set" as a success.

## Files

- `app.py` — Streamlit UI (thin, calls `data_helpers.py`)
- `data_helpers.py` — pure data-shaping functions, no Streamlit import, unit-tested in `tests/test_dashboard_helpers.py`
- `../generators/decision_support.py` — aggregated Gate status, lever ranking, recommendation (`tests/test_decision_support.py`)
- `../generators/demo_scenarios.py` + `../data/demo_scenarios.yaml` — named example scenarios (`tests/test_demo_scenarios.py`)
- `../generators/green_gates.py` — Gate-zone classification, shared by both the dashboard and `decision_support.py`
- Smoke-tested end-to-end via Streamlit's `AppTest` harness in `tests/test_dashboard_app.py`
