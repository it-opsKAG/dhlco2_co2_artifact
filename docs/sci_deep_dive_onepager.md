# SCI Deep Dive (One‑Pager, Phase 1)

Status: draft (deterministic, assumption‑first)  
Source: SCI Specification v1.1.0 (local copy in OneDrive) + DHLCO2 Phase‑1 decisions

## Goal

Provide a Phase‑1 compatible SCI summary that is directly usable for the DHLCO2 KPI candidates and traceable to current project decisions.

## SCI equation (rate)

We use the project baseline equation (see also `Projects/dhlco2_co2_artifact/data/assumptions_proxies.yaml`):

`SCI = ((E * I) + M) / R`

## Terms (Phase‑1 operational meaning)

- `E` (Energy): Energy consumed by the software system within the agreed **software boundary** and **time window**.
  - Phase‑1 approach: derive `E` from infrastructure / runtime telemetry where available; otherwise from billing/usage models (explicitly marked as proxies).
- `I` (Carbon intensity): Carbon intensity of electricity for the region (and ideally time) where `E` is consumed.
  - Phase‑1 status: provider selection is **TBD** (tracked as `GAP-001` in `Projects/dhlco2_co2_artifact/exports/Gap_Report.md`).
- `M` (Embodied emissions): Embodied emissions of the hardware required to operate the software within boundary.
  - Phase‑1 approach: treat embodied emissions as **candidate** and apply an explicit amortization model.
  - Phase‑1 status: amortization method is **TBD** (tracked as `GAP-003`).
- `R` (Functional unit): Denominator that makes SCI a **rate** (not a total).
  - Phase‑1: `R1` is decided for build KPIs; `R2` is TBD for run KPIs (tracked as `GAP-002`).

## Build vs Run boundary (Phase‑1 decision)

Canonical decision pack: `Projects/dhlco2_co2_artifact/docs/decision_packs/phase1_initial/decisions.yaml` (`build_vs_run_boundary`).

- Build in scope: CI/CD pipeline runs, test environments, build minutes per artifact, ML training in development, embodied amortization in development context.
- Run in scope: inference + operational service requests, data transfer in operation, energy proportionality, region/time carbon‑intensity weighting.
- Edge cases: release/deploy treated as run‑adjacent unless executed purely inside CI/CD.

## Measurement vs calculation

Phase‑1 supports two modes per component inside the boundary:

- Measurement: measure total carbon over a time window, divide by `R` in the same window.
- Calculation/model: model “one unit of R” and compute carbon for that modeled execution; clearly separate assumptions.

Phase‑1 rule: if real‑world data is not available, use proxies (see `Projects/dhlco2_co2_artifact/exports/Gap_Report.md`) and mark output quality explicitly.

## Exclusions (Phase‑1)

- Offsetting/neutralization mechanisms do not reduce SCI; only emission elimination reduces SCI.
- Full hardware validation measurements are out of scope for Phase‑1 (explicitly in decisions).

## Open decisions (kept explicit)

1. Carbon intensity provider + sampling/fallback policy (`GAP-001`)
2. Run functional unit `R2` definition + counting method + data owners (`GAP-002`, `GAP-004`)
3. Embodied amortization model + inventory source (`GAP-003`)
4. KPI ISO reference mapping (`GAP-005`)

