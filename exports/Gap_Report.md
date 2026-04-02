# Gap Report

## Declared Gaps

| ID | Title | Impact | Required Input | Status | Source Refs |
| --- | --- | --- | --- | --- | --- |
| GAP-001 | Carbon intensity provider — phased integration model defined | Phase 1 calculations use documented simplified values; precision increases with each integration step. | Standort-/Regionsinformationen des Auftraggebers für Phase-2-Integration. | addressed | DHLCO2-4; DHLCO2-11 |
| GAP-002 | Functional unit R2 — decided (service request) | Run KPI denominators are now methodically defined; operative data binding is subject of implementation phase. | Stakeholder alignment on monitoring system for request counting (Phase 2). | addressed | DHLCO2-8; DHLCO2-11 |
| GAP-003 | Embodied carbon amortization method undefined | Indirect emission KPIs cannot move past candidate state. | Define amortization model and inventory source. | open_phase2 | DHLCO2-4; DHLCO2-10 |
| GAP-004 | Data ownership and source systems undefined | No deterministic production pipeline can be connected. | Assign owner and system per KPI candidate (requires stakeholder input). | open_phase2 | DHLCO2-6; DHLCO2-10; DHLCO2-11 |
| GAP-005 | ISO reference mapping incomplete | Normative traceability is incomplete. | Complete mapping to agreed standards per KPI. | open_phase2 | DHLCO2-6; DHLCO2-7; Offer para 62 |

## Proxies

| ID | Gap ID | Proxy | Quality | Source Refs |
| --- | --- | --- | --- | --- |
| PRX-001 | GAP-001 | Use region-level average grid intensity feed until source is fixed. | low | DHLCO2-11 |
| PRX-002 | GAP-002 | Use request count as temporary denominator for RUN-001 to RUN-004. | low | DHLCO2-8; DHLCO2-11 |
| PRX-003 | GAP-003 | Use linear amortization over fixed service life. | low | DHLCO2-4; DHLCO2-10 |
| PRX-004 | GAP-004 | Use ticket assignee as temporary owner until RACI is defined. | low | DHLCO2-6 |

## Derived TBD Entries

- `assumptions_doc.gaps[4].description`: KPI-level ISO references are marked TBD in ticket drafts.
- `kpis_doc.kpis[0].accounting_boundary`: Candidate boundary: one CI/CD pipeline run including runner compute and allocated cloud usage; shared-runner allocation remains TBD.
- `kpis_doc.kpis[0].data_sources[0]`: CI logs (TBD system name)
- `kpis_doc.kpis[0].data_sources[1]`: Runner metrics (TBD metric ids)
- `kpis_doc.kpis[0].data_sources[2]`: Cloud billing/usage (TBD account scope)
- `kpis_doc.kpis[0].feedback_latency`: TBD until source-system bindings and reporting cadence are fixed.
- `kpis_doc.kpis[0].iso_refs[0]`: TBD
- `kpis_doc.kpis[0].representation_risk`: Proxy use; shared-runner allocation uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[0].unknowns[0]`: Carbon intensity source is TBD.
- `kpis_doc.kpis[0].unknowns[1]`: Shared runner allocation rule is TBD.
- `kpis_doc.kpis[1].accounting_boundary`: Candidate boundary: test environment operation window allocated to test-hours; cross-team allocation remains TBD.
- `kpis_doc.kpis[1].data_sources[0]`: Test environment telemetry (TBD provider)
- `kpis_doc.kpis[1].data_sources[1]`: Infrastructure metrics (TBD metric ids)
- `kpis_doc.kpis[1].data_sources[2]`: Cloud billing/usage (TBD account scope)
- `kpis_doc.kpis[1].feedback_latency`: TBD until environment telemetry bindings and reporting cadence are fixed.
- `kpis_doc.kpis[1].iso_refs[0]`: TBD
- `kpis_doc.kpis[1].representation_risk`: Proxy use; boundary uncertainty; cross-team allocation uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[1].unknowns[0]`: Test environment boundary is TBD.
- `kpis_doc.kpis[1].unknowns[1]`: Allocation across teams is TBD.
- `kpis_doc.kpis[2].accounting_boundary`: Candidate boundary: build and release activity per artifact or release event; artifact granularity remains TBD.
- `kpis_doc.kpis[2].data_sources[0]`: CI logs (TBD build stage granularity)
- `kpis_doc.kpis[2].data_sources[1]`: Artifact registry metrics (TBD source)
- `kpis_doc.kpis[2].feedback_latency`: TBD until build-stage bindings and release-event cadence are fixed.
- `kpis_doc.kpis[2].iso_refs[0]`: TBD
- `kpis_doc.kpis[2].representation_risk`: Proxy use; artifact granularity uncertainty; energy-conversion uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[2].unknowns[0]`: Artifact granularity is TBD.
- `kpis_doc.kpis[2].unknowns[1]`: Energy conversion from build minutes is TBD.
- `kpis_doc.kpis[3].accounting_boundary`: Candidate boundary: one training run including workload telemetry and allocated hardware contribution; attribution remains TBD.
- `kpis_doc.kpis[3].data_sources[0]`: Training telemetry (TBD platform)
- `kpis_doc.kpis[3].data_sources[1]`: GPU/CPU metrics (TBD metric ids)
- `kpis_doc.kpis[3].data_sources[2]`: Cloud billing/usage (TBD account scope)
- `kpis_doc.kpis[3].feedback_latency`: TBD until training telemetry bindings and reporting cadence are fixed.
- `kpis_doc.kpis[3].iso_refs[0]`: TBD
- `kpis_doc.kpis[3].representation_risk`: Proxy use; hardware amortization uncertainty; training attribution uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[3].unknowns[0]`: Training boundary and attribution are TBD.
- `kpis_doc.kpis[3].unknowns[1]`: Embodied carbon treatment for hardware is TBD.
- `kpis_doc.kpis[4].accounting_boundary`: Candidate boundary: hardware embodied emissions allocated to planning increments or story points; amortization method remains TBD.
- `kpis_doc.kpis[4].data_sources[0]`: Hardware inventory (TBD source)
- `kpis_doc.kpis[4].data_sources[1]`: Lifecycle amortization table (TBD method)
- `kpis_doc.kpis[4].data_sources[2]`: Planning system story points (TBD source)
- `kpis_doc.kpis[4].feedback_latency`: TBD until inventory source, planning binding, and refresh cadence are fixed.
- `kpis_doc.kpis[4].iso_refs[0]`: TBD
- `kpis_doc.kpis[4].representation_risk`: Amortization uncertainty; normalization uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[4].unknowns[0]`: Amortization method is TBD.
- `kpis_doc.kpis[4].unknowns[1]`: Story-point normalization is TBD.
- `kpis_doc.kpis[5].data_sources[0]`: APM traces (TBD source)
- `kpis_doc.kpis[5].data_sources[1]`: Operational logs (TBD source)
- `kpis_doc.kpis[5].feedback_latency`: TBD until APM/log bindings and reporting cadence are fixed.
- `kpis_doc.kpis[5].iso_refs[0]`: TBD
- `kpis_doc.kpis[5].representation_risk`: Proxy use; transaction taxonomy uncertainty; operative request-count binding TBD; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[5].unknowns[0]`: Transaction definition boundary is TBD (R2a service-request decided for Phase 1; extension to business-level units planned).
- `kpis_doc.kpis[5].unknowns[1]`: Operative data source for request counting is TBD (requires stakeholder alignment on monitoring system).
- `kpis_doc.kpis[6].accounting_boundary`: Candidate boundary: request-level system boundary per service request; operative counter system remains TBD.
- `kpis_doc.kpis[6].data_sources[0]`: Service metrics (TBD source)
- `kpis_doc.kpis[6].data_sources[1]`: Infrastructure metrics (TBD metric ids)
- `kpis_doc.kpis[6].feedback_latency`: TBD until service/infrastructure bindings and reporting cadence are fixed.
- `kpis_doc.kpis[6].iso_refs[0]`: TBD
- `kpis_doc.kpis[6].representation_risk`: Proxy use; request-boundary uncertainty; operative denominator binding TBD; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[6].unknowns[0]`: Request boundary definition is TBD (R2a decided; operative system TBD).
- `kpis_doc.kpis[6].unknowns[1]`: Carbon intensity: Phase 1 uses national averages; sampling strategy for Phase 2+ is TBD.
- `kpis_doc.kpis[7].accounting_boundary`: Candidate boundary: data transfer within a defined service boundary per GB; internal versus external split remains TBD.
- `kpis_doc.kpis[7].data_sources[0]`: Network metrics (TBD source)
- `kpis_doc.kpis[7].data_sources[1]`: Data egress billing (TBD source)
- `kpis_doc.kpis[7].feedback_latency`: TBD until network and billing bindings plus reporting cadence are fixed.
- `kpis_doc.kpis[7].iso_refs[0]`: TBD
- `kpis_doc.kpis[7].representation_risk`: Proxy use; service-boundary uncertainty; traffic-split uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[7].unknowns[0]`: Service boundary for transfer accounting is TBD (R2a decided; operative system TBD).
- `kpis_doc.kpis[7].unknowns[1]`: Internal vs external traffic split is TBD.
- `kpis_doc.kpis[8].data_sources[0]`: Utilization metrics (TBD source)
- `kpis_doc.kpis[8].data_sources[1]`: Power draw metrics (TBD source)
- `kpis_doc.kpis[8].feedback_latency`: TBD until observation windows, thresholds, and reporting cadence are fixed.
- `kpis_doc.kpis[8].iso_refs[0]`: TBD
- `kpis_doc.kpis[8].representation_risk`: Proxy use; threshold-definition uncertainty; interval-definition uncertainty; source-system identifiers TBD; ISO mapping incomplete.
- `kpis_doc.kpis[8].unknowns[0]`: Threshold definition is TBD (R2a decided; operative calibration TBD).
- `kpis_doc.kpis[8].unknowns[1]`: Measurement interval is TBD.
