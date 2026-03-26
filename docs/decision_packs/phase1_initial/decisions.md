# Phase 1 Decisions

## Summary

- Canonical artifact home is this repository.
- Functional units: `R1: 1 CI/CD pipeline run` (decided) and `R2: 1 service request` (decided 2026-03-26, with extension path to business-level units).
- Build and run are separated per offer references and documented boundary decision (BVR-001).
- CO₂ intensity data: three-stage integration model defined (national averages → IEA/EMBER → Electricity Maps).

## Rationale

1. Build KPI candidates (BLD-001 to BLD-005) cover CI/CD, test environments, ML training, and embodied carbon.
2. Run KPI candidates (RUN-001 to RUN-004) cover operational workloads, energy proportionality, and data transfer.
3. SCI baseline formula ((E × I) + M) / R is applied consistently across all KPIs.
4. Gaps and proxies are explicitly tracked with quality ratings.
5. Phase 1 deliverables: KPI Catalog, Lifecycle Mapping, Framework Overview, Measurement Matrix, Standards Positioning.

## Deployment Boundary Edge Cases

| Edge ID | Scenario | Assignment | Why |
| --- | --- | --- | --- |
| EDGE-001 | Pre-production load test in CI | build | Executed in pipeline and used for release gating. |
| EDGE-002 | Canary deployment in production | run | Runs on production infrastructure with operational traffic. |
| EDGE-003 | Shared artifact registry traffic | TBD | Requires formal allocation policy across build/run consumers. |

## Open Items (deferred to Phase 2)

- Embodied carbon amortization method is not fixed (GAP-003).
- Data ownership and source systems require stakeholder alignment (GAP-004).
- ISO clause mapping remains to be completed at KPI level (GAP-005).

