# DHLCO2 CO2 Artifact (Phase 1)

Canonical artifact home for DHLCO2 Phase 1.

## Scope

- Keep canonical data in `data/`.
- Validate structure with `schema/kpis.schema.json`.
- Generate deterministic exports with `generators/build_exports.py`.
- Run local CI flow with `ci/validate_and_export.py`.

## Local Run

```bash
python ci/validate_and_export.py
```

## Promote From Staging

Preview pending promotions (default gate: committed files only):

```bash
python ci/promote_from_staging.py
```

Apply promotions and update registry:

```bash
python ci/promote_from_staging.py --apply
```

Override approval gate (for explicit worktree-driven review):

```bash
python ci/promote_from_staging.py --approval-mode worktree
```

Scan all run folders for untransferred committed content:

```bash
python ci/promote_from_staging.py --source-run-dir outputs/dhlco2_phase1
```
