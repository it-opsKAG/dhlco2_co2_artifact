# Gap Report

## Declared Gaps

| ID | Title | Impact | Required Input | Status | Source Refs |
| --- | --- | --- | --- | --- | --- |
| GAP-001 | Carbon intensity provider undefined | SCI outputs cannot be finalized for build or run KPIs. | Select provider, granularity, and fallback policy. | open | DHLCO2-4; DHLCO2-11 |
| GAP-002 | Functional unit R2 undefined | Run KPI denominators remain provisional. | Decide R2 and counting method. | open | DHLCO2-8; DHLCO2-11 |
| GAP-003 | Embodied carbon amortization method undefined | Indirect emission KPIs cannot move past candidate state. | Define amortization model and inventory source. | open | DHLCO2-4; DHLCO2-10 |
| GAP-004 | Data ownership and source systems undefined | No deterministic production pipeline can be connected. | Assign owner and system per KPI candidate. | open | DHLCO2-6; DHLCO2-10; DHLCO2-11 |
| GAP-005 | ISO reference mapping incomplete | Normative traceability is incomplete. | Complete mapping to agreed standards per KPI. | open | DHLCO2-6; DHLCO2-7; Offer para 62 |

## Proxies

| ID | Gap ID | Proxy | Quality | Source Refs |
| --- | --- | --- | --- | --- |
| PRX-001 | GAP-001 | Use region-level average grid intensity feed until source is fixed. | low | DHLCO2-11 |
| PRX-002 | GAP-002 | Use request count as temporary denominator for RUN-001 to RUN-004. | low | DHLCO2-8; DHLCO2-11 |
| PRX-003 | GAP-003 | Use linear amortization over fixed service life. | low | DHLCO2-4; DHLCO2-10 |
| PRX-004 | GAP-004 | Use ticket assignee as temporary owner until RACI is defined. | low | DHLCO2-6 |

## Derived TBD Entries

- `assumptions_doc.gaps[4].description`: KPI-level ISO references are marked TBD in ticket drafts.
- `kpis_doc.kpis[0].data_sources[0]`: CI logs (TBD system name)
- `kpis_doc.kpis[0].data_sources[1]`: Runner metrics (TBD metric ids)
- `kpis_doc.kpis[0].data_sources[2]`: Cloud billing/usage (TBD account scope)
- `kpis_doc.kpis[0].iso_refs[0]`: TBD
- `kpis_doc.kpis[0].unknowns[0]`: Carbon intensity source is TBD.
- `kpis_doc.kpis[0].unknowns[1]`: Shared runner allocation rule is TBD.
- `kpis_doc.kpis[1].data_sources[0]`: Test environment telemetry (TBD provider)
- `kpis_doc.kpis[1].data_sources[1]`: Infrastructure metrics (TBD metric ids)
- `kpis_doc.kpis[1].data_sources[2]`: Cloud billing/usage (TBD account scope)
- `kpis_doc.kpis[1].iso_refs[0]`: TBD
- `kpis_doc.kpis[1].unknowns[0]`: Test environment boundary is TBD.
- `kpis_doc.kpis[1].unknowns[1]`: Allocation across teams is TBD.
- `kpis_doc.kpis[2].data_sources[0]`: CI logs (TBD build stage granularity)
- `kpis_doc.kpis[2].data_sources[1]`: Artifact registry metrics (TBD source)
- `kpis_doc.kpis[2].iso_refs[0]`: TBD
- `kpis_doc.kpis[2].unknowns[0]`: Artifact granularity is TBD.
- `kpis_doc.kpis[2].unknowns[1]`: Energy conversion from build minutes is TBD.
- `kpis_doc.kpis[3].data_sources[0]`: Training telemetry (TBD platform)
- `kpis_doc.kpis[3].data_sources[1]`: GPU/CPU metrics (TBD metric ids)
- `kpis_doc.kpis[3].data_sources[2]`: Cloud billing/usage (TBD account scope)
- `kpis_doc.kpis[3].iso_refs[0]`: TBD
- `kpis_doc.kpis[3].unknowns[0]`: Training boundary and attribution are TBD.
- `kpis_doc.kpis[3].unknowns[1]`: Embodied carbon treatment for hardware is TBD.
- `kpis_doc.kpis[4].data_sources[0]`: Hardware inventory (TBD source)
- `kpis_doc.kpis[4].data_sources[1]`: Lifecycle amortization table (TBD method)
- `kpis_doc.kpis[4].data_sources[2]`: Planning system story points (TBD source)
- `kpis_doc.kpis[4].iso_refs[0]`: TBD
- `kpis_doc.kpis[4].unknowns[0]`: Amortization method is TBD.
- `kpis_doc.kpis[4].unknowns[1]`: Story-point normalization is TBD.
- `kpis_doc.kpis[5].data_sources[0]`: APM traces (TBD source)
- `kpis_doc.kpis[5].data_sources[1]`: Operational logs (TBD source)
- `kpis_doc.kpis[5].data_sources[2]`: Carbon intensity feed (TBD provider)
- `kpis_doc.kpis[5].functional_unit`: R2: candidate (TBD)
- `kpis_doc.kpis[5].iso_refs[0]`: TBD
- `kpis_doc.kpis[5].unknowns[0]`: Functional unit R2 is TBD.
- `kpis_doc.kpis[5].unknowns[1]`: Transaction definition is TBD.
- `kpis_doc.kpis[6].data_sources[0]`: Service metrics (TBD source)
- `kpis_doc.kpis[6].data_sources[1]`: Infrastructure metrics (TBD metric ids)
- `kpis_doc.kpis[6].data_sources[2]`: Carbon intensity feed (TBD provider)
- `kpis_doc.kpis[6].functional_unit`: R2: candidate (TBD)
- `kpis_doc.kpis[6].iso_refs[0]`: TBD
- `kpis_doc.kpis[6].unknowns[0]`: Request denominator and boundary are TBD.
- `kpis_doc.kpis[6].unknowns[1]`: Carbon intensity sampling strategy is TBD.
- `kpis_doc.kpis[7].data_sources[0]`: Network metrics (TBD source)
- `kpis_doc.kpis[7].data_sources[1]`: Data egress billing (TBD source)
- `kpis_doc.kpis[7].data_sources[2]`: Carbon intensity feed (TBD provider)
- `kpis_doc.kpis[7].functional_unit`: R2: candidate (TBD)
- `kpis_doc.kpis[7].iso_refs[0]`: TBD
- `kpis_doc.kpis[7].unknowns[0]`: Service boundary for transfer accounting is TBD.
- `kpis_doc.kpis[7].unknowns[1]`: Internal vs external traffic split is TBD.
- `kpis_doc.kpis[8].data_sources[0]`: Utilization metrics (TBD source)
- `kpis_doc.kpis[8].data_sources[1]`: Power draw metrics (TBD source)
- `kpis_doc.kpis[8].functional_unit`: R2: candidate (TBD)
- `kpis_doc.kpis[8].iso_refs[0]`: TBD
- `kpis_doc.kpis[8].unknowns[0]`: Threshold definition is TBD.
- `kpis_doc.kpis[8].unknowns[1]`: Measurement interval is TBD.
