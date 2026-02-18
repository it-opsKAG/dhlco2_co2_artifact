# DHLCO2 – Phase 1 Project One‑Pager (Draft)

## Objective

Create a scientifically grounded, Phase‑1 “CO₂ Emissions Monitoring” artifact for the software lifecycle (Build & Run) that is comparable, traceable, and decision‑ready (not a tool/product build).

## Phase‑1 deliverables (current repo SSOT)

- KPI Catalog: `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.md` + `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.csv`
- Lifecycle Mapping: `Projects/dhlco2_co2_artifact/exports/Lifecycle_Mapping.md`
- Gap Report (unknowns + proxies): `Projects/dhlco2_co2_artifact/exports/Gap_Report.md`
- Decisions (boundary + functional units): `Projects/dhlco2_co2_artifact/docs/decision_packs/phase1_initial/decisions.yaml`

Supporting drafts:

- SCI One‑Pager: `Projects/dhlco2_co2_artifact/docs/sci_deep_dive_onepager.md`
- Functional units (R candidates): `Projects/dhlco2_co2_artifact/docs/functional_units_r_candidates.md`

## Current status (as of 2026‑02‑18)

- Canonical data model + exports exist and validate (Phase‑1 initial).
- Open gaps are explicitly tracked; key blockers are provider selection for carbon intensity and run functional unit `R2`.

## Open decisions / blockers (explicit)

1. `GAP-001`: Carbon intensity provider + sampling/fallback policy
2. `GAP-002`: Run functional unit `R2` + deterministic counting method
3. `GAP-003`: Embodied carbon amortization model + inventory source
4. `GAP-004`: Data ownership/source systems per KPI (telemetry boundary)
5. `GAP-005`: ISO reference mapping per KPI

## Next steps (Phase‑1, deterministic)

1. Decide `R2` (or accept proxy) + document counting rule and owner.
2. Decide carbon intensity feed requirements (granularity, regions, cadence) and shortlist providers.
3. Promote the three generated exports + the two supporting drafts into Vault as “promoted summaries”.

