# Roadmap — DHLCO2 CO₂-Artefakt

**Projekt:** CO₂-Emissions-Monitoring-Framework für den Software-Lifecycle bei DHL Express  
**Auftraggeber:** DHL Express / Krallmann AG  
**Methodische Grundlage:** GSF SCI Specification v1.1.0, ISO 14064-1:2018  
**Repo-Rolle:** Single Source of Truth (SSOT) für KPI-Definitionen, Modelle, Entscheidungen und Exporte

---

## Übergeordnetes Ziel

Ein **wissenschaftlich belastbares, reproduzierbares CO₂-Mess- und Steuerungssystem** für DHL-Softwareprojekte, das:

1. Build- und Run-Emissionen quantifiziert (nach SCI-Formel)
2. In bestehende DevOps-Prozesse integriert werden kann (Green Gates, Maturity Model)
3. Datengetrieben optimierbar ist (Simulation, Pareto-Auswahl von Infrastruktur)
4. Audit-fähig und normativ rückverfolgbar ist (ISO 14064-1, GHG Protocol)

---

## Phasenübersicht

```
Phase 1  ████████████████████  ✅ Abgeschlossen (2026-05-13)
Phase 2  █████████████████░░░  🔄 In Bearbeitung (~85%, alle 6 Dokument-Deliverables fertig; offen: DHL-Review + Pilot-Scope)
Phase 3  ░░░░░░░░░░░░░░░░░░░░  🔲 Geplant
Phase 4  ░░░░░░░░░░░░░░░░░░░░  🔲 Langfrist
```

---

## Phase 1 — Framework & Entscheidungsgrundlage ✅

**Abgeschlossen:** 2026-05-13  
**Deliverables:** Alle 9 Deliverables (DEL-001 bis DEL-009) geliefert

Was Phase 1 geliefert hat:
- 19 KPI-Kandidaten vollständig definiert (SCI, BLD, RUN, INF, GOV, HW)
- Build/Run-Grenze entschieden (Edge Cases EDGE-001 bis EDGE-003)
- Functional Units entschieden: R1 = 1 CI/CD-Run, R2a = 1 Service-Request
- Standards-Positioning: ISO 14064-1 als primäre Norm, ISO 14083 als Referenz
- Deterministischer Export-Generator (kpis.yaml → 7 Exportartefakte)
- GAP-003 (Embodied Carbon Methode) definiert, PRX-003 auf medium gehoben
- Hardware-CO₂-Modell: `generators/hardware_model.py` (EfficiencyScore, RDC-Stub)
- Simulation-Runner: `generators/simulation_runner.py` (192 Szenarien, Stellvariablen)
- Green Gates: `data/green_gates.yaml` (alle 19 KPIs, grün/amber/rot)
- Instrumentation Backlog: `docs/phase2_instrumentation_backlog.md` (Tier 0/1/2)

---

## Phase 2 — Prozessintegration & Pilot-Vorbereitung 🔄

**Ziel:** CO₂-KPIs in DevOps-Prozesse einbetten; Pilot A (Build) + Pilot B (Run) instrumentieren  
**Angebot:** `00_Projektmanagement/03_Projektangebote/2026-05-07_DHLCO2_Phase2_Vorgehensvorschlag.md`

### Deliverables Status

| # | Deliverable | Datei | Status |
|---|---|---|---|
| D2-01 | Prozessintegrationsmodell | `docs/phase2_process_integration_model.md` | ✅ done (2026-06-29) |
| D2-02 | Design Principles + Green Gates | `data/green_gates.yaml` + `docs/phase2_design_principles.md` | ✅ done (2026-07-14) |
| D2-03 | KPI-to-Process-Mapping | `docs/phase2_kpi_to_process_mapping.md` + `data/kpi_process_mapping.yaml` | ✅ done (2026-07-14) |
| D2-04 | Best Practices | `docs/phase2_best_practices.md` | ✅ done (2026-07-14) |
| D2-05 | Instrumentation Backlog Tier 0/1/2 | `docs/phase2_instrumentation_backlog.md` | ✅ done |
| D2-06 | Aktualisierte Gap-Analyse | `docs/phase2_rdc_gap_analysis.md` | ✅ done (GAP-003 closed) |

### Offene Klärungspunkte mit DHL (Blocker)

| ID | Frage | Auswirkung |
|---|---|---|
| OC-01 | Welche Pipeline ist Pilot A? | Tier-0 T0-01 geblockt |
| OC-02 | Welcher Service ist Pilot B? | Tier-0 T0-02/T0-04 geblockt |
| OC-03 | Welches RZ / Cloud-Region? | Carbon Intensity Feed (T0-03) |
| OC-04 | Vorhandene APM-Lösung? | T0-04 (OTel vs. Datadog vs. Dynatrace) |
| OC-05 | RACI-Rollen besetzen | 6 Rollen definiert in `data/green_gates.yaml` |

### Milestones Phase 2

| Milestone | Bedingung | Zieldatum |
|---|---|---|
| **M2-A: Deliverables vollständig** | D2-01, D2-03, D2-04 fertig | ✅ erreicht 2026-07-14 (unabhängig vom Stakeholder-Workshop) |
| **M2-B: Pilot-Scope entschieden** | OC-01 bis OC-05 geklärt | Stakeholder-Workshop |
| **M2-C: Phase 2 abgenommen** | Alle 6 Deliverables, Stakeholder-Review done | TBD — Deliverables fertig, Review von DHL ausstehend |

---

## Phase 3 — Operationalisierung & Dashboard 🔲

**Voraussetzung:** Phase 2 abgeschlossen, Pilot-Scope bestätigt  
**Konzept:** `docs/phase3_simulation_concept.md`

### Geplante Deliverables

| # | Deliverable | Beschreibung |
|---|---|---|
| D3-01 | Live-Telemetrie Pilot A | Eco-CI + Tier-0-Tooling produktiv für Pilot-Pipeline |
| D3-02 | Live-Telemetrie Pilot B | Kepler/Scaphandre + OTel für Pilot-Service |
| D3-03 | KPI-Berechnung automatisiert | Scheduler, der täglich KPI-Werte berechnet und speichert |
| D3-04 | Dashboard v1 | Grafana: Engineering / Platform / Management View |
| D3-05 | Green Gate Integration | Automatischer Release-Block bei anhaltenden Roten Gates |
| D3-06 | Simulation Live-Feed | simulation_runner.py mit echten Telemetriedaten als Input |
| D3-07 | Maturity-Assessment | Alle Pilot-KPIs auf M2 (automatisiert/beobachtbar) |

### Milestones Phase 3

| Milestone | Bedingung |
|---|---|
| **M3-A: Pilot A live** | BLD-001 liefert echte Zahlen aus CI-Pipeline |
| **M3-B: Pilot B live** | RUN-001/002 liefern echte Zahlen aus Run-Service |
| **M3-C: Dashboard v1** | Alle 3 Views befüllt, intern reviewt |
| **M3-D: Phase 3 abgenommen** | Stakeholder-Review, Audit-Readiness GOV-002 ≥ M2 |

### Infrastruktur-Fortschritt, unabhängig vom Pilot-Scope-Blocker (2026-07-10)

D3-06 (Simulation Live-Feed) braucht als Vorstufe eine echte Multi-Objective-Optimierung statt
der reinen Single-Score-Sortierung in `rdc_rank()`. Diese Vorstufe ist jetzt gebaut, unabhängig
von OC-01 bis OC-05 (Pilot-Scope-Klärung mit DHL bleibt weiterhin blockierend für D3-01 bis D3-05):

- `generators/rdc_pareto.py` (neu): echte Pareto-Frontier über CO2/Request, EUR/Request und
  EfficiencyScore + Sensitivitätsanalyse (Δco2/ΔStellvariable), aufbauend auf der generischen
  `adaptive_decision_kernel.optimization`-Bibliothek statt einer DHL-lokalen Implementierung.
- Repo ist jetzt `uv`-verwaltbar (`pyproject.toml` neu, additiv — bestehende
  `ci/validate_and_export.py`-Pipeline unverändert).
- Vollständiger Kontext, offene Folge-Runs und die Cross-Repo-Einordnung (dieses Vorhaben ist
  Teil eines größeren Enterprise-Simulation-Vorhabens über mehrere Repos):
  `docs/enterprise_simulation_roadmap.md`.

---

## Phase 4 — Skalierung & Echtzeit 🔲

**Voraussetzung:** Phase 3 abgeschlossen

| Vorhaben | Beschreibung |
|---|---|
| Electricity Maps API | Stündlicher, regionaler Carbon-Intensity-Feed (ersetzt UBA-Proxy) |
| DCGM-Exporter | GPU-VRAM/Power live aus Cluster (HW-001 live statt Proxy) |
| Org-weite Ausrollung | Alle Pipelines + Services (Tier-2 Instrumentation Backlog). Erster Schritt bereits 2026-07-15 gemacht: Eco-CI-Energiemessung auf 6 von 51 eigenen Repos ausgerollt (Portfolio-Inventur + Auswahlkriterien: `docs/phase3_data_source_roadmap.md` §1a) — Nachweis, dass die Methodik technologieunabhängig portierbar ist. |
| Allocation Policy Registry | GOV-003 auf M3 (audit-capable) |
| ISO-14064-1 Audit | Formale Auditierung des Frameworks |

---

## Technische Schulden & bekannte Lücken

| ID | Beschreibung | Priorität |
|---|---|---|
| TD-01 | `embodied_co2_kg: null` in allen hardware_configs — Vendor-PCF-Datasheets fehlen | Mittel |
| TD-02 | GAP-004 (Data Ownership) noch offen — keine RACI-Besetzung | Hoch (Blocker Phase 3) |
| TD-03 | GAP-005 (ISO-Mapping) noch offen — KPI-Level-ISO-Refs sind TBD | Mittel |
| TD-04 | Simulation nutzt noch keine echten Telemetriedaten | Mittel (Phase 3) |
| TD-05 | `simulation_runner.py` schreibt in `exports/` (gitignored) — kein Artifact-Store | ✅ geschlossen 2026-07-14: `generators/evidence_ledger.py` stempelt jeden Lauf mit RUN-ID, Git-Commit und SHA-256-Hashes der Outputs in `evidence/` (committed, klein) — CSV/MD bleiben gitignored und reproduzierbar, aber der Lauf selbst ist jetzt zitierbar |

---

## Repo-Struktur (Übersicht)

```
dhlco2_co2_artifact/
├── data/                      # SSOT — alle Daten hier, nicht in Docs
│   ├── kpis.yaml              # 19 KPI-Kandidaten (SCI/BLD/RUN/INF/GOV/HW)
│   ├── assumptions_proxies.yaml  # 3 Assumptions, 5 Gaps, 4 Proxies
│   ├── lifecycle_mapping.yaml # KPI-to-Lifecycle (8 Steps, 19 Mappings)
│   ├── hardware_configs.yaml  # 6 generische Infrastruktur-Tiers + EfficiencyScore-Gewichte
│   └── green_gates.yaml       # grün/amber/rot Schwellenwerte für alle 19 KPIs
├── schema/
│   └── kpis.schema.json       # JSON-Schema (strikt, 28 Pflichtfelder je KPI)
├── generators/
│   ├── build_exports.py       # Deterministischer Export-Generator
│   ├── hardware_model.py      # EfficiencyScore, CO2-Modell, RDC-Stub
│   └── simulation_runner.py   # Stellvariablen-Simulation (Szenario-Sweep)
├── ci/
│   └── validate_and_export.py # CI-Einstiegspunkt (Schema + Export-Check)
├── docs/
│   ├── phase2_rdc_gap_analysis.md        # Gap-Analyse RDC-Konzept vs Repo
│   ├── phase2_instrumentation_backlog.md # Tier 0/1/2 Tooling-Backlog
│   ├── phase3_simulation_concept.md      # RDC-Operator-Spezifikation
│   ├── decision_packs/phase1_initial/    # Phase-1-Entscheidungsdokumentation
│   └── slr/phase1_initial/              # Standards-Mapping, Evidenzledger
├── exports/                   # Generiert — gitignored, reproduzierbar per CI
├── ROADMAP.md                 # ← diese Datei
└── NEXT_STEPS.md              # Konkrete nächste Tasks (sofort umsetzbar)
```
