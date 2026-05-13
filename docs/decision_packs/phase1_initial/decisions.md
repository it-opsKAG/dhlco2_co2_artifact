# Phase 1 Decisions

## Summary

- Canonical artifact home is this repository.
- Functional units: `R1: 1 CI/CD pipeline run` (decided) and `R2: 1 service request` (decided 2026-03-26, with extension path to business-level units).
- Build and run are separated per offer references and documented boundary decision (BVR-001).
- CO₂ intensity data: three-stage integration model defined (national averages → IEA/EMBER → Electricity Maps).

## Rationale

1. Core SCI KPI candidates (SCI-001 to SCI-002) anchor the software-carbon rate and the reporting-period total.
2. Build KPI candidates (BLD-001 to BLD-005) cover CI/CD, test environments, ML training, and embodied carbon.
3. Run KPI candidates (RUN-001 to RUN-004) cover operational workloads, energy proportionality, and data transfer.
4. Infrastructure Context KPI candidates (INF-001 to INF-003) cover PUE, CUE, and utilization context.
5. Data Quality & Governance KPI candidates (GOV-001 to GOV-003) cover completeness, maturity, and allocation-policy compliance.
6. SCI baseline formula ((E × I) + M) / R is applied consistently where the KPI expresses software-carbon intensity.
7. Gaps and proxies are explicitly tracked with quality ratings.
8. Phase 1 deliverables: KPI Catalog, Lifecycle Mapping, Framework Overview, Measurement Matrix, Standards Positioning.

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
