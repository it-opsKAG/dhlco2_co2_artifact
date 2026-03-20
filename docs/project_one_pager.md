# DHLCO2 - Phase 1 Project One-Pager (Draft)

## Objective

Create a scientifically grounded Phase-1 CO2 emissions monitoring artifact for the software lifecycle (Build and Run) that is comparable, traceable, and decision-ready, without pretending Phase 1 is already a production tool rollout.

## Contribution of the framework

- Gives DHL one consistent method backbone across build and run instead of isolated metric fragments.
- Separates decided content, temporary proxies, and real blockers so review can focus on the right decisions.
- Keeps customer-facing outputs tied to the same SSOT that later enables operational rollout and simulation.

## Phase-1 artifact structure (current repo SSOT)

- Framework Overview: `Projects/dhlco2_co2_artifact/exports/Framework_Overview.md`
- KPI Catalog: `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.md` + `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.csv`
- Measurement Matrix: `Projects/dhlco2_co2_artifact/exports/Measurement_Matrix.md`
- Lifecycle Mapping: `Projects/dhlco2_co2_artifact/exports/Lifecycle_Mapping.md`
- Gap Report (unknowns + proxies): `Projects/dhlco2_co2_artifact/exports/Gap_Report.md`
- Decisions (boundary + functional units): `Projects/dhlco2_co2_artifact/docs/decision_packs/phase1_initial/decisions.yaml`

Supporting drafts:

- SCI One-Pager: `Projects/dhlco2_co2_artifact/docs/sci_deep_dive_onepager.md`
- Functional units (R candidates): `Projects/dhlco2_co2_artifact/docs/functional_units_r_candidates.md`

## Customer-feedback fold-in for artifact vNext

1. Artifact structure is now made explicit via `Framework_Overview.md`.
2. KPI concreteness is made more reviewable via `KPI_Catalog.md` plus KPI-level measurement metadata.
3. Functional-unit clarity remains explicit: `R1` is fixed, `R2` stays open but governed via proxy and decision path.
4. Data sources and measurement logic are consolidated in `Measurement_Matrix.md`.
5. The framework value statement is surfaced here instead of being scattered across status reports.

## Current status (as of 2026-03-20)

- Canonical data model and exports exist and validate.
- Build and run KPI candidates are structured enough for a customer-facing vNext artifact.
- The remaining blockers are explicit and narrow enough to drive focused review instead of broad rework.

## Open decisions / blockers (explicit)

1. `GAP-001`: Carbon intensity provider plus sampling and fallback policy
2. `GAP-002`: Run functional unit `R2` plus deterministic counting method
3. `GAP-003`: Embodied carbon amortization model plus inventory source
4. `GAP-004`: Data ownership and authoritative source systems per KPI
5. `GAP-005`: KPI-level ISO reference mapping

## Next steps (Phase 1, deterministic)

1. Review `Framework_Overview.md` and `Measurement_Matrix.md` against customer feedback.
2. Decide `R2` or formally accept the current proxy and document owner plus counting rule.
3. Shortlist carbon-intensity provider options and lock the policy boundary for build and run KPIs.
