# Functional Units (R) – Phase 1 Candidates

Status: draft (decision‑ready)

Canonical Phase‑1 decision pack: `Projects/dhlco2_co2_artifact/docs/decision_packs/phase1_initial/decisions.yaml` (`functional_units`).

## R1 (Build) – decided

- ID: `R1`
- Label: `1 CI/CD pipeline run`
- Counting method (Phase‑1): count pipeline executions from CI system run logs; optionally segment by pipeline/job type.
- Primary use: Build KPIs (`BLD-*` in `Projects/dhlco2_co2_artifact/data/kpis.yaml`).

## R2 (Run) – candidates (TBD decision)

Phase‑1 principle: pick an `R2` that is (a) observable deterministically from telemetry and (b) meaningful enough as a denominator for run‑phase KPI candidates.

### Candidate set

| Candidate | Definition | Counting method (deterministic) | Likely data source | Pros | Cons |
| --- | --- | --- | --- | --- | --- |
| R2a: 1 service request | One handled request at the system boundary (API call / operation) | Counter increment per request at boundary; exclude internal retries unless explicitly modeled | APM traces + gateway logs | Easy to measure; aligns with `RUN-002` | Business meaning varies by endpoint; needs boundary definition |
| R2b: 1 transaction | One business transaction (higher-level than request) | Derive from trace attributes / domain event id | APM + domain events | Business-aligned; aligns with `RUN-001` | Harder to define consistently; needs event taxonomy |
| R2c: 1 shipment | One shipment processed (business unit) | Count shipments in domain system and map to software boundary | Domain systems | Very intuitive to DHL | Often crosses multiple systems; attribution is complex |
| R2d: 1 scan/tracking event | One scan event (ops unit) | Count scanner events + map to software system | Event streams/logs | Concrete, high-volume | Boundary mapping may be partial; duplicates |
| R2e: 1 optimization run | One route/plan optimization execution | Count job executions | Job scheduler logs | Clear for specific workloads | Too narrow for general run KPIs |

### Phase‑1 proxy recommendation (to unblock RUN KPIs)

Until `R2` is decided, use the existing project proxy (`PRX-002` in `Projects/dhlco2_co2_artifact/data/assumptions_proxies.yaml`):

- Proxy: request count as temporary denominator for `RUN-001..RUN-004`
- Quality: low (explicitly marked)

## Decision checklist (what to lock next)

1. Select `R2` (or formally accept proxy for Phase‑1 demo).
2. Define boundary: which requests/transactions count, and what is excluded (retries, internal calls).
3. Assign data owner + authoritative source system for the counter (`GAP-004`).

