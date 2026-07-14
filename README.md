# DHLCO2 CO₂-Artefakt

**CO₂-Emissions-Monitoring-Framework für den Software-Lifecycle bei DHL Express**  
Auftraggeber: DHL Express · Konsultant: Krallmann AG  
Methodik: GSF SCI Specification v1.1.0 · ISO 14064-1:2018

---

## Was dieses Repo ist

Ein **wissenschaftlich belastbares, reproduzierbares Mess-Framework** für Software-CO₂-Emissionen.  
Keine Produktionssoftware — ein Entscheidungs- und Planungsinstrument:

- **19 KPI-Kandidaten** von Build-Pipeline bis Hardware-Amortisierung
- **Deterministischer Export-Generator**: YAML → Markdown/CSV in einem Befehl
- **Hardware-CO₂-Modell**: EfficiencyScore, Embodied-Carbon-Rechner, Infrastruktur-Vergleich
- **Simulation**: 192 parametrisierte Szenarien über Workload, Energie-Mix und Traffic
- **Green Gates**: grün/amber/rot Schwellenwerte für alle 19 KPIs

---

## Schnellstart

```bash
# Exports regenerieren + Schema validieren
PYTHONUTF8=1 python ci/validate_and_export.py

# Infrastruktur-Simulation (1728 Szenarien seit TASK-05, davor 192)
PYTHONUTF8=1 python generators/simulation_runner.py

# Hardware-Modell direkt
PYTHONUTF8=1 python generators/hardware_model.py
```

**Dependencies:** `pip install pyyaml jsonschema`  
**Hinweis:** `exports/` ist gitignored — immer lokal regenerieren.

---

## Einstieg für neue Sitzungen

| Ich will... | Datei |
|---|---|
| Wissen was als nächstes zu tun ist | **`NEXT_STEPS.md`** |
| Die Gesamtstrategie verstehen | **`ROADMAP.md`** |
| KPIs einsehen oder ändern | `data/kpis.yaml` |
| Green Gates anpassen | `data/green_gates.yaml` |
| Hardware-Tiers anpassen | `data/hardware_configs.yaml` |
| Gaps und offene Punkte sehen | `data/assumptions_proxies.yaml` |
| Simulation-Parameter ändern | `generators/simulation_runner.py` → `SCENARIO_AXES` |

---

## Phasenstatus

| Phase | Inhalt | Status |
|---|---|---|
| **Phase 1** | KPI-Framework, Functional Units, Standards-Positioning | ✅ Abgeschlossen |
| **Phase 2** | Prozessintegration, Pilot-Vorbereitung, Green Gates | 🔄 ~60% |
| **Phase 3** | Live-Telemetrie, Dashboard, Green Gate Integration | 🔲 Geplant |
| **Phase 4** | Org-weite Skalierung, Echtzeit-CO₂-Feed, Audit | 🔲 Langfrist |

---

## Repo-Struktur

```
dhlco2_co2_artifact/
├── ROADMAP.md                 # Strategie, Phasen, Milestones
├── NEXT_STEPS.md              # Konkrete Tasks — hier einsteigen
├── data/                      # SSOT — alle definierten Daten
│   ├── kpis.yaml              # 19 KPI-Kandidaten
│   ├── assumptions_proxies.yaml  # Gaps, Proxies, Assumptions
│   ├── lifecycle_mapping.yaml # KPI ↔ Lifecycle-Schritt Mappings
│   ├── hardware_configs.yaml  # Infrastruktur-Tiers (generisch)
│   └── green_gates.yaml       # Schwellenwerte je KPI
├── schema/
│   └── kpis.schema.json       # JSON-Schema (28 Pflichtfelder je KPI)
├── generators/
│   ├── build_exports.py       # YAML → Markdown/CSV Export
│   ├── hardware_model.py      # CO₂- und Kostenmodell, RDC-Stub
│   └── simulation_runner.py   # Stellvariablen-Szenario-Sweep
├── ci/
│   └── validate_and_export.py # CI: Schema + Exports prüfen
├── docs/
│   ├── phase2_rdc_gap_analysis.md        # Gap-Analyse RDC-Konzept
│   ├── phase2_instrumentation_backlog.md # Tier-0/1/2 Tooling-Plan
│   ├── phase3_simulation_concept.md      # Simulationskonzept Phase 3
│   ├── decision_packs/phase1_initial/    # Phase-1-Entscheidungen
│   └── slr/phase1_initial/              # Standards-Mapping, SLR
└── exports/                   # Generiert — nicht committen
```

## Kauffman Context
KRS: 52/100 (intentionally low — deterministic consulting artifact).
Highest Kauffman dimension: Constraint Closure (D2: 7/10) via SCI formula, Green-Gate policy, JSON schema strict validation.
Adjacent Possible: this artifact can pivot to a live CO2 telemetry feed for the adaptive_* ecosystem.
See [KAUFFMAN_ROADMAP.md](KAUFFMAN_ROADMAP.md) for integration proposals.
