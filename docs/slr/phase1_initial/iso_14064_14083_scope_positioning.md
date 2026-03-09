# Normative Scope Positioning: ISO 14064-1 and ISO 14083

Status: final draft for DHL study artifact  
Checked against official sources: 2026-03-09

## Purpose

This note consolidates the normative positioning for the DHLCO2 study artifact and fixes the scope distinction between `ISO 14064-1` and `ISO 14083`.

## Consolidated position

`ISO 14064-1:2018` is the more appropriate overarching frame for the DHL study artifact. The official ISO catalog defines it as the organization-level specification with guidance for quantification and reporting of greenhouse gas emissions and removals. That fits the project objective to quantify, attribute, aggregate, and document emissions across projects, shared digital infrastructure, and organizational units in a way that remains auditable and governance-ready.

`ISO 14083:2023` remains relevant, but with a narrower scope. The official ISO catalog defines it as the standard for quantification and reporting of greenhouse gas emissions arising from transport chain operations. For DHL Express this makes it highly relevant for road, air, and multimodal transport emissions. For the study artifact developed here, however, it is not the primary normative basis, because the artifact does not primarily calculate physical transport-chain emissions. Its main purpose is to create a fine-grained attribution model for digital infrastructure, project-related system landscapes, and shared ICT resources.

The clean positioning for the study is therefore:

- `ISO 14064-1` as the primary methodological umbrella for inventory logic, reporting discipline, traceability, and verification readiness.
- `GHG Protocol Corporate Standard` as the complementary accounting logic for organizational boundaries and Scope 1/2/3 framing.
- `ISO 14083` as the transport-specific reference point for physical logistics emissions and as a benchmark for transparency and granularity, not as the main standard for the digital artifact itself.

If later project stages quantify intervention effects or require external assurance, `ISO 14064-2` (project-level GHG changes) and `ISO 14064-3` (validation and verification of GHG statements) become the relevant extensions.

## Recommended wording for the study

ISO 14083 is relevant for our context insofar as it standardizes the quantification and reporting of greenhouse gas emissions along physical transport chains and thus provides a robust reference frame for transport-related emissions in logistics environments such as DHL Express. At the same time, the artifact developed in this study addresses a different and complementary problem class: not primarily the emissions of physical transport, but the fine-grained, cross-project capture, attribution, and aggregation of emission-relevant contributions within the digital infrastructure and system landscape of a logistics enterprise. While ISO 14083 therefore provides methodological depth for the physical transport path, our approach establishes a comparable basis of transparency for digital processes, IT resources, services, and system dependencies that are not sufficiently covered by classical transport standards. For this broader purpose, ISO 14064-1 is the more suitable methodological umbrella because it structures greenhouse gas quantification and reporting at organizational level and thereby supports a wider inventory, attribution, and governance context.

## Why ISO 14083 is not the primary standard for this artifact

- It is transport-chain specific by design.
- It is strongest where emissions arise from physical logistics operations.
- It does not by itself solve attribution problems for shared compute, software services, data flows, or cross-project digital dependencies.
- It remains useful in the introduction and motivation section as the physical-scope reference point against which the study's digital contribution is delimited.

## Recommended normative stack for Phase 1

| Layer | Recommended standard or reference | Role in the DHL study artifact |
| --- | --- | --- |
| Governance and inventory frame | ISO 14064-1:2018 | Organization-level quantification, reporting, documentation, and verification readiness |
| Accounting logic | GHG Protocol Corporate Standard | Organizational boundary logic and Scope 1/2/3 framing |
| Transport-specific benchmark | ISO 14083:2023 | Reference for physical transport-chain emissions and granularity expectations |
| ICT-specific allocation support | GHG Protocol ICT Sector Guidance | Secondary support for shared-resource and ICT allocation questions |
| Future extension: interventions | ISO 14064-2 | Quantification of project-level emission reductions or removals |
| Future extension: assurance | ISO 14064-3 | Validation and verification of GHG statements |

## Source references

Primary sources used for this positioning:

1. ISO. `ISO 14064-1:2018` catalog page. Official title: "Greenhouse gases — Part 1: Specification with guidance at the organization level for quantification and reporting of greenhouse gas emissions and removals." Accessed 2026-03-09.  
   URL: https://www.iso.org/standard/66453.html
2. ISO. `ISO 14083:2023` catalog page. Official title: "Greenhouse gases — Quantification and reporting of greenhouse gas emissions arising from transport chain operations." Accessed 2026-03-09.  
   URL: https://www.iso.org/standard/78806.html
3. GHG Protocol. `A Corporate Accounting and Reporting Standard (Revised Edition)`. Used for organizational-boundary and scope framing. Accessed 2026-03-09.  
   URL: https://ghgprotocol.org/corporate-standard
4. GHG Protocol. `ICT Sector Guidance`. Used as secondary support for ICT allocation and shared-resource challenges. Accessed 2026-03-09.  
   URL: https://ghgprotocol.org/ict-sector-guidance

## Relation to existing repo artifacts

- Standards overview: `Projects/dhlco2_co2_artifact/docs/slr/phase1_initial/standards_map.md`
- Current gap tracking: `Projects/dhlco2_co2_artifact/exports/Gap_Report.md`
- Functional-unit decisions: `Projects/dhlco2_co2_artifact/docs/functional_units_r_candidates.md`
- Project framing: `Projects/dhlco2_co2_artifact/docs/project_one_pager.md`
