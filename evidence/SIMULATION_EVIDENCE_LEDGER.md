# Simulation Evidence Ledger

Append-only record of simulation runs. Each row is independently reproducible: check out the referenced git commit, re-run `generators/evidence_ledger.py`, and confirm the output hashes match. This ledger backs the scenario/row-count figures quoted in customer-facing materials with a concrete, auditable artifact instead of a bare number.

| Run ID | Created (UTC) | Git Commit | Dirty | Scenarios | Rows | HW Configs | CSV SHA-256 (short) |
|---|---|---|---|---|---|---|---|
| RUN-20260713T221421Z-SIM-fullsweep | 2026-07-13T22:14:21+00:00 | `a670b049dfc4` | True | 192 | 816 | 6 | `a26ca6080896` |
| RUN-20260714T170658Z-SIM-boavizta-embodied | 2026-07-14T17:06:58+00:00 | `ac5096ee97d4` | True | 192 | 816 | 6 | `dbf04eac41d5` |
| RUN-20260714T210542Z-SIM-task05-more-stellvariablen | 2026-07-14T21:05:42+00:00 | `70b300829364` | True | 1728 | 7344 | 6 | `c7352e9ffab7` |

## Full manifests

See `evidence/simulation_runs.jsonl` (one JSON manifest per line) for the complete record per run, including the exact scenario-axis parameters and full SHA-256 hashes.
