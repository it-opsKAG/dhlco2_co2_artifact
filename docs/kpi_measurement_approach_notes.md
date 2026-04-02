# KPI Measurement Approach Notes (Phase 1)

Status: draft (implementation-ready notes; assumptions explicit)

This document sharpens the "measurement approach" layer of the KPI catalog for
Phase 1. Canonical KPI definitions remain in:

- `Projects/dhlco2_co2_artifact/data/kpis.yaml`
- `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.csv`

## Cross-cutting rule (SCI baseline)

All KPI candidates use the baseline SCI rate:

`SCI = ((E * I) + M) / R`

Phase 1 supports:

- **Measurement mode**: derive `E` (and optionally `M`) from real telemetry or billing over a time window and divide by `R` in the same window.
- **Model mode**: model one unit of `R` and compute `(E, I, M)` via controlled measurement or explicit proxy assumptions.

## Cross-cutting review fields

Each KPI should now be read not only as a formula candidate but as a
measurement-and-control artifact. The following review fields are therefore
explicit:

- **Represented state**: which physical or operational burden the KPI is intended to make visible.
- **Accounting boundary**: which system slice is included and which allocation questions remain open.
- **Representation risk**: proxy use, boundary uncertainty, source-system gaps, normalization risks, and incomplete standard mapping.
- **Data coverage**: current posture of the KPI data basis. Phase 1 is generally `partial`.
- **Feedback latency**: how quickly the KPI can become decision-relevant once source-system bindings are fixed.
- **Decision lever**: which concrete operational or governance decision the KPI is intended to inform.

## Build KPIs (`BLD-*`)

### BLD-001 – CI/CD pipeline emissions per run

- Represented state: emissions attributable to one CI/CD pipeline run.
- Measurement: sum runner energy or compute from runtime and power model; multiply by `I`; add allocated `M`.
- Accounting boundary: one pipeline run including runner compute and allocated cloud usage; shared-runner allocation remains TBD.
- Representation risk: proxy use, shared-runner allocation uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until CI and billing bindings plus reporting cadence are fixed.
- Decision lever: pipeline scheduling, runner selection, and shared-runner allocation policy.

### BLD-002 – Test environment emissions per test-hour

- Represented state: emissions attributable to test-environment operation.
- Measurement: attribute energy of test resources to a test window; normalize by test-hours or by run if coupled to a pipeline.
- Accounting boundary: test-environment operation window allocated to test-hours; cross-team allocation remains TBD.
- Representation risk: proxy use, boundary uncertainty, cross-team allocation uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until environment telemetry bindings and reporting cadence are fixed.
- Decision lever: test-environment runtime, sizing, and shutdown policy.

### BLD-003 – Build minutes per artifact

- Represented state: build effort as an energy-relevant proxy at artifact level.
- Measurement: use build duration as proxy when direct power telemetry is unavailable; validate via spot measurements.
- Accounting boundary: build and release activity per artifact or release event; artifact granularity remains TBD.
- Representation risk: proxy use, artifact granularity uncertainty, energy-conversion uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until build-stage bindings and release-event cadence are fixed.
- Decision lever: build-stage optimization, artifact packaging, and release frequency.

### BLD-004 – ML training emissions per run

- Represented state: operational and allocated embodied impact of model-training runs.
- Measurement: collect GPU/CPU utilization plus run duration; attribute to training run id; compute energy; apply `I`; add allocated `M`.
- Accounting boundary: one training run including workload telemetry and allocated hardware contribution; attribution remains TBD.
- Representation risk: proxy use, hardware amortization uncertainty, training attribution uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until training telemetry bindings and reporting cadence are fixed.
- Decision lever: training frequency, hardware selection, and run-gating policy.

### BLD-005 – Embodied carbon amortization per story point

- Represented state: indirect build-related emissions from embodied hardware footprint.
- Measurement: amortize embodied emissions of relevant hardware over service life and allocate to workload; normalize by story points.
- Accounting boundary: hardware embodied emissions allocated to planning increments or story points; amortization method remains TBD.
- Representation risk: amortization uncertainty, normalization uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until inventory source, planning binding, and refresh cadence are fixed.
- Decision lever: hardware refresh policy, amortization policy, and planning normalization.

## Run KPIs (`RUN-*`)

Phase 1 denominator posture:

- `R2a = 1 service request` is the Phase-1 reference unit.
- Extension path remains explicit: Phase 2 can move toward business transaction (`R2b`) and later shipment-based units (`R2c`) once operative data is available.

### RUN-001 – Emissions per transaction

- Represented state: full run-phase emissions attributable to one service request or future business transaction boundary.
- Measurement: attribute operational energy plus allocated embodied share to the request or transaction boundary; divide by counted units.
- Accounting boundary: operational service-request scope in Phase 1 with extension path to business transaction.
- Representation risk: proxy use, transaction taxonomy uncertainty, operative request-count binding TBD, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until APM/log bindings and reporting cadence are fixed.
- Decision lever: transaction design, service optimization, and boundary selection.

### RUN-002 – Energy per request

- Represented state: request-level operational energy demand.
- Measurement: attribute energy consumption to request counts at the defined system boundary; divide Wh by request count.
- Accounting boundary: request-level system boundary per service request; operative counter system remains TBD.
- Representation risk: proxy use, request-boundary uncertainty, operative denominator binding TBD, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until service and infrastructure bindings plus reporting cadence are fixed.
- Decision lever: request efficiency, autoscaling, and infrastructure right-sizing.

### RUN-003 – Data transfer emissions per GB

- Represented state: transfer-related operational burden from network traffic and data egress.
- Measurement: use network byte counters or egress billing; convert to energy where needed; apply `I`; normalize by GB.
- Accounting boundary: data transfer within a defined service boundary per GB; internal versus external split remains TBD.
- Representation risk: proxy use, service-boundary uncertainty, traffic-split uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until network and billing bindings plus reporting cadence are fixed.
- Decision lever: payload size, egress routing, and caching strategy.

### RUN-004 – Energy proportionality index

- Represented state: inefficiency under low or variable utilization.
- Measurement: compare utilization versus power or energy at different load levels; output ratio or index.
- Accounting boundary: observation window or service slice for utilization-versus-power comparison.
- Representation risk: proxy use, threshold-definition uncertainty, interval-definition uncertainty, source-system identifiers TBD, ISO mapping incomplete.
- Feedback latency: TBD until observation windows, thresholds, and reporting cadence are fixed.
- Decision lever: capacity right-sizing, utilization targets, and workload placement.

## Minimum implementation questions per KPI

Before a KPI moves beyond candidate state, the following questions should be
explicitly answerable:

1. What physical or operational burden is the KPI intended to represent?
2. What is inside the accounting boundary, and what is outside?
3. Which data sources are direct measurements, and which are proxies?
4. What is the expected reporting cadence and feedback latency?
5. Which decision will change if the KPI moves materially?
