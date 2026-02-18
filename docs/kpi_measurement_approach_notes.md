# KPI Measurement Approach Notes (Phase 1)

Status: draft (implementation‑ready notes; assumptions explicit)

This document clarifies the “measurement approach” part of the KPI catalog for Phase‑1. Canonical KPI definitions remain in:

- `Projects/dhlco2_co2_artifact/data/kpis.yaml`
- `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.csv`

## Cross‑cutting rule (SCI baseline)

All KPI candidates use the baseline SCI rate:

`SCI = ((E * I) + M) / R`

Phase‑1 supports:

- **Measurement mode**: derive `E` (and optionally `C`) from real telemetry/billing over a time window and divide by `R` in the same window.
- **Model mode**: model one unit of `R` and compute (E, I, M) via controlled measurement or best estimates (marked as proxy).

## Build KPIs (`BLD-*`)

### BLD-001 – CI/CD pipeline emissions per run
- Measurement: sum runner energy (or compute from CPU time * power model) per pipeline run; multiply by `I`; add amortized `M` allocation.
- Required counters: pipeline run id → jobs/steps; runtime duration; runner type; region/time.

### BLD-002 – Test environment emissions per test-hour
- Measurement: attribute energy of test env resources to a test window; normalize by test-hours (or per run if coupled to pipeline).
- Required counters: env on/off windows; resource allocation; region/time.

### BLD-003 – Build minutes per artifact
- Model/proxy: use build duration as proxy for energy when direct power telemetry is unavailable; validate via spot measurements.
- Required counters: artifact id; build stage durations; artifact registry events.

### BLD-004 – ML training emissions per run
- Measurement: collect GPU/CPU utilization + run duration; attribute to training run id; compute energy; apply `I`; add amortized `M`.
- Required counters: training run id; hardware type; region/time; utilization traces.

### BLD-005 – Embodied carbon amortization per story point
- Model: amortize embodied emissions of relevant hardware over service life and allocate to workload; normalize by story points.
- Required inputs: inventory list; service life model; allocation rule; planning system story points.

## Run KPIs (`RUN-*`)

Phase‑1 proxy for denominator: request count until `R2` is decided (see `PRX-002` in `Projects/dhlco2_co2_artifact/data/assumptions_proxies.yaml`).

### RUN-001 – Emissions per transaction
- Measurement: attribute operational energy + embodied allocation to a transaction boundary (ideally domain event); divide by transaction count.
- Required counters: transaction id taxonomy; mapping from traces/logs to transaction.

### RUN-002 – Energy per request
- Measurement: attribute energy consumption to request counts at the system boundary; divide Wh by request count.
- Required counters: request counter; boundary definition; sampling interval.

### RUN-003 – Data transfer emissions per GB
- Measurement: use network byte counters / billing egress; convert to energy where needed; apply `I`; normalize by GB.
- Required counters: internal vs external traffic split; boundary mapping.

### RUN-004 – Energy proportionality index
- Measurement: compare utilization vs power (or energy) at different load levels; output ratio/index.
- Required counters: utilization metrics; power/energy metrics; defined interval + threshold policy.

