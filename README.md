# DHLCO2 CO2 Artifact (Phase 1)

Canonical artifact home for DHLCO2 Phase 1.

## Scope

- Keep canonical data in `data/`.
- Validate structure with `schema/kpis.schema.json`.
- Generate deterministic exports with `generators/build_exports.py`.
- Run local CI flow with `ci/validate_and_export.py`.

## Current reference notes

- Normative scope positioning for the DHL study: `docs/slr/phase1_initial/iso_14064_14083_scope_positioning.md`
- Phase-1 standards overview: `docs/slr/phase1_initial/standards_map.md`

## Local Run

```bash
python ci/validate_and_export.py
```

## Staging Transfer

Promotion and archive automation is centralized in `system/tools` and profile-driven via:

- `system/tools/staging_promote_cli.py`
- `system/tools/staging_archive_cli.py`
- `system/registry/staging_transfer_profiles.v1.yaml`
