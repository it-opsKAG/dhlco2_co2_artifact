# ENTSO-E Live Verification & Integration — Handoff

Prepared: 2026-07-15. Status: **security token now available** (registration + email
request done earlier; token just arrived). Live verification and integration have
**not** been executed yet — this doc prepares a clean, self-contained start for a
fresh session, per the same "clean handoff" pattern used for the earlier CI-lint-debt
and findability-benchmark handoffs in this project family.

## 1. What already exists (built and unit-tested against a synthetic fixture only)

- `generators/entsoe_grid_carbon.py` — the connector. Key pieces:
  - `fetch_generation_mix(security_token=..., zone_eic=..., period_start=, period_end=)`
    → calls `https://web-api.tp.entsoe.eu/api` with `documentType=A75&processType=A16`
    (actual generation per production type), default window = last 2 hours.
  - `parse_generation_mix_xml()` — namespace-agnostic XML parsing (never captured a
    real response yet, only the documented shape).
  - `compute_weighted_carbon_intensity()` — weights each PSR (fuel) type's generation
    by a documented IPCC AR5 / Fraunhofer-ISE emission-factor table
    (`PSR_EMISSION_FACTORS_GCO2E_PER_KWH`), falls back to 485 gCO2e/kWh (UBA 2024 DE
    average) for unmapped codes.
  - `BIDDING_ZONES = {"DE_LU": "10Y1001A1001A83F"}` — only Germany/Luxembourg wired
    so far.
  - `main()` reads `ENTSOE_SECURITY_TOKEN` from the environment and prints a
    human-readable snapshot; prints a clear "token not set" message otherwise.
- `tests/test_entsoe_grid_carbon.py` — 5 unit tests pass today against a synthetic
  XML fixture (parsing, weighting, unmapped-PSR flagging, fallback behavior). One
  more test, `test_fetch_generation_mix_smoke`, is marked `@pytest.mark.live` and is
  **skipped by default** — it needs a real token and makes a real network call.
- `docs/phase3_data_source_roadmap.md` §1 and `NEXT_STEPS.md` TASK-12 both describe
  this as blocked on the token, with the exact next command already written down:
  `ENTSOE_SECURITY_TOKEN=... uv run pytest tests/test_entsoe_grid_carbon.py -m live`.

## 2. Token handling — do not paste the token into chat or commit it anywhere

- `.env` is already in `.gitignore`, but **no script in this repo auto-loads a
  `.env` file** — there is no `python-dotenv` dependency anywhere in this project's
  own code (confirmed via grep; the only `dotenv` hits are inside third-party
  packages under `.venv`). So the simplest path is a **shell-session environment
  variable**, set directly by the user in their own terminal, never typed into the
  chat:
  - bash: `export ENTSOE_SECURITY_TOKEN=<token>`
  - PowerShell: `$env:ENTSOE_SECURITY_TOKEN = "<token>"`
- If persistence across sessions is wanted, that's a separate, explicit decision
  (e.g., add `python-dotenv` + a `.env` loader) — don't add it silently as a side
  effect of this task.

## 3. Step-by-step for the new session

1. Confirm the token is set without ever printing its value:
   `python -c "import os; print(bool(os.getenv('ENTSOE_SECURITY_TOKEN')))"` → `True`.
2. Run the live unit test: `uv run pytest tests/test_entsoe_grid_carbon.py -m live -v`
   → expect 1 passed.
3. Run the connector directly for a human-readable real snapshot:
   `PYTHONUTF8=1 python generators/entsoe_grid_carbon.py` — capture zone, period
   window, weighted CO2 factor, and any unmapped PSR codes printed.
4. For comparison, also run the already-live energy-charts.info signal at the same
   time: `PYTHONUTF8=1 python generators/live_grid_carbon.py`. Record all three
   numbers side by side: ENTSO-E (new), energy-charts.info (existing), static UBA-2024
   baseline (485 gCO2e/kWh).
5. Document the real result in `docs/phase3_data_source_roadmap.md` §1 — mirror
   exactly how §2 (Eco-CI) recorded its first real run as a markdown table (see the
   "Erster echter Lauf" table there): zone, period, weighted intensity, unmapped PSR
   codes if any, three-way comparison from step 4.
6. Update `NEXT_STEPS.md` TASK-12: status from `In Arbeit 2026-07-15` to
   `Done + live verifiziert <date>`, replace the "Blocker" line with the real result
   summary (mirror TASK-13's done-state formatting immediately below it).
7. **Recommended, low-risk:** wire the connector into the dashboard's existing
   "Live-Kontext" tab (`dashboard/app.py`, the `fetch_live_grid_carbon_intensity()`
   call around line 259) as a second live data point next to the existing
   energy-charts.info one — same defensive pattern (try/except around the network
   call, clear fallback message, never crash the dashboard offline). This makes the
   regulatorisch-autoritative EU source demoable live, not just written down.
8. **Do not** wire ENTSO-E into the core KPI/simulation calculation
   (`generators/hardware_model.py`, `generators/simulation_runner.py`) in this pass.
   This repo's established convention (see `generators/live_grid_carbon.py`'s own
   docstring) is that live external signals stay demo/context-only until a
   carbon-intensity provider policy is formally decided for GAP-001
   (`docs/phase2_rdc_gap_analysis.md`). If the user wants to go further — e.g.
   empirically recalibrate `SCENARIO_AXES["grid_ef_gco2e_per_kwh"]` in
   `simulation_runner.py` from ENTSO-E historical time series instead of the current
   hand-set round numbers (485/295/100) — treat that as a separate, explicitly
   requested follow-up, not an automatic part of "the token arrived."
9. Run the full test suite to confirm nothing else broke:
   `PYTHONUTF8=1 uv run pytest` (fall back to the CI's pip-based subset — see
   `.github/workflows/energy-ci.yml` — if `uv sync` hits the known
   `adaptive-decision-kernel` private-repo issue again).
10. Once the user confirms the real numbers look plausible (expect the weighted
    intensity somewhere between the solar factor ~41 and worst-case fossil ~1054
    gCO2e/kWh — most likely 250-550 gCO2e/kWh for DE_LU depending on time of day/
    season), commit and push.

## 4. Open judgment calls — ask the user, don't assume

- Persist the token via `.env` + a loader for convenience, or keep it a per-session
  shell export? Either is fine; it's a workflow preference, not decided here.
- Should the Friday-facing presentation (`Slides DHL Statusupdate Juli 2026 - v2
  (Demonstrator, Governance-Ausblick).pptx` in OneDrive, or a v3) reference the new
  live ENTSO-E number? Not this handoff's call.
- Extend `BIDDING_ZONES` beyond `DE_LU`? Only relevant once Pilot B's region is
  confirmed — still blocked on OC-01..OC-05 (business flags, unrelated to this task).

## 5. References

- `generators/entsoe_grid_carbon.py`, `tests/test_entsoe_grid_carbon.py`
- `generators/live_grid_carbon.py` (sibling live signal, already dashboard-wired —
  copy its defensive/error-handling pattern)
- `dashboard/app.py` (~line 44 import, ~line 259 "Live-Kontext" tab)
- `docs/phase3_data_source_roadmap.md` §1 (ENTSO-E) and §2 (Eco-CI, the precedent for
  how to record a first real external measurement)
- `NEXT_STEPS.md` TASK-12 (current blocked status), TASK-13 (done-state formatting
  precedent)
- `docs/phase2_rdc_gap_analysis.md` (GAP-001, why live signals stay context-only for
  now)
