# Phase 1 Decisions

## Summary

- Canonical artifact home is `repo`.
- Promotion policy is `repo -> vault -> jira`.
- Functional units are `R1: 1 CI/CD pipeline run` (decided) and `R2: candidate (TBD)`.
- Build and run are separated per ticket evidence and offer references.

## Rationale

1. Ticket `DHLCO2-10` defines build KPI candidates with CI/CD, test, and training focus.
2. Ticket `DHLCO2-11` defines run KPI candidates with operational workload focus.
3. Ticket `DHLCO2-4` states SCI baseline and the need to decide boundaries and allocation.
4. Ticket `DHLCO2-6` states explicit gap handling and proxy requirements.
5. Ticket `DHLCO2-7` states the three required deliverables for Phase 1.

## Deployment Boundary Edge Cases

| Edge ID | Scenario | Assignment | Why |
| --- | --- | --- | --- |
| EDGE-001 | Pre-production load test in CI | build | Executed in pipeline and used for release gating. |
| EDGE-002 | Canary deployment in production | run | Runs on production infrastructure with operational traffic. |
| EDGE-003 | Shared artifact registry traffic | TBD | Requires formal allocation policy across build/run consumers. |

## Open Items

- `R2` is not selected yet and blocks finalized run KPI denominators.
- Carbon intensity provider and refresh policy are not selected.
- Embodied carbon amortization method is not fixed.
- ISO clause mapping remains `TBD` at KPI level.

