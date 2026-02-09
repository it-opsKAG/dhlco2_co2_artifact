# Manifest

Stable run id: `phase1_initial`

## Repo Artifacts (`Projects/dhlco2_co2_artifact/`)

- `Projects/dhlco2_co2_artifact/README.md` - Repository-level usage and execution entrypoint.
- `Projects/dhlco2_co2_artifact/ci/ci.local.yaml` - Minimal local CI step definition.
- `Projects/dhlco2_co2_artifact/ci/validate_and_export.py` - Local runner to validate and regenerate exports.
- `Projects/dhlco2_co2_artifact/ci/validate_and_export.sh` - Shell wrapper for local runner.
- `Projects/dhlco2_co2_artifact/data/assumptions_proxies.yaml` - Canonical assumptions, gaps, and proxy catalog.
- `Projects/dhlco2_co2_artifact/data/kpis.yaml` - Canonical Phase 1 KPI candidate dataset.
- `Projects/dhlco2_co2_artifact/data/lifecycle_mapping.yaml` - Canonical lifecycle and KPI-step mapping.
- `Projects/dhlco2_co2_artifact/docs/phase1_scope.md` - SSOT scope and promotion stance for Phase 1.
- `Projects/dhlco2_co2_artifact/exports/Gap_Report.md` - Deterministic gap and TBD consolidation.
- `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.csv` - Machine-readable KPI export.
- `Projects/dhlco2_co2_artifact/exports/KPI_Catalog.md` - Human-readable KPI catalog export.
- `Projects/dhlco2_co2_artifact/exports/Lifecycle_Mapping.md` - Human-readable lifecycle mapping export.
- `Projects/dhlco2_co2_artifact/generators/build_exports.py` - Deterministic export generator.
- `Projects/dhlco2_co2_artifact/schema/kpis.schema.json` - JSON schema for KPI dataset validation.

## Staging Outputs (`staging/outputs/dhlco2_phase1/phase1_initial/`)

- `staging/outputs/dhlco2_phase1/phase1_initial/decisions.md` - Human-readable Phase 1 decisions and edge cases.
- `staging/outputs/dhlco2_phase1/phase1_initial/decisions.yaml` - Machine-readable decision pack.
- `staging/outputs/dhlco2_phase1/phase1_initial/manifest.md` - File manifest for this deterministic run.
- `staging/outputs/dhlco2_phase1/phase1_initial/slr/evidence_ledger.yaml` - Claim-to-source ledger template with starter entries.
- `staging/outputs/dhlco2_phase1/phase1_initial/slr/exclusion_criteria.md` - SLR exclusion rules.
- `staging/outputs/dhlco2_phase1/phase1_initial/slr/inclusion_criteria.md` - SLR inclusion rules.
- `staging/outputs/dhlco2_phase1/phase1_initial/slr/query_pack.yaml` - Theme-grouped initial SLR query pack.
- `staging/outputs/dhlco2_phase1/phase1_initial/slr/standards_map.md` - Standards mapping matrix for Phase 1 needs.
