# Next Steps — DHLCO2 CO₂-Artefakt

**Letzte Aktualisierung:** 2026-07-10  
**Phase:** 2 (In Bearbeitung, ~60%); Phase-3-Vorstufe (Pareto/Sensitivität) zusätzlich gestartet, siehe TASK-08  
**Vollständige Roadmap:** `ROADMAP.md` · **Cross-Repo-Vorhaben:** `docs/enterprise_simulation_roadmap.md`

Dieses Dokument ist der Einstiegspunkt für die nächste Arbeitssitzung.  
Kein Kontextwissen nötig — alles Nötige steht hier oder ist verlinkt.

---

## Erledigt (nicht mehr TODO, hier als Kontext für den nächsten Schritt)

### TASK-08 · RDC-Pareto-Optimierung (D3-06-Vorstufe) `Done 2026-07-10`
**Dateien:** `generators/rdc_pareto.py`, `tests/test_rdc_pareto.py`, `pyproject.toml` (neu)  
**Was:** `rdc_rank()` sortierte bisher nur nach einer einzigen Dimension (EfficiencyScore).
`rdc_pareto.py` baut daraus eine echte Pareto-Frontier über CO2/Request, EUR/Request und
EfficiencyScore, plus Sensitivitätsanalyse (Δco2/ΔStellvariable), aufbauend auf der neuen,
domänenneutralen `adaptive_decision_kernel.optimization`-Bibliothek. `rdc_rank()` selbst bleibt
unverändert (additive Erweiterung, kein Rewrite). Details: `docs/enterprise_simulation_roadmap.md`.

## Sofort umsetzbar — keine DHL-Abstimmung nötig

### TASK-09 · Volle Phase-3-SimulationEngine `Enhancement, Nachfolger von TASK-08`
**Datei:** `generators/rdc_pareto.py` erweitern oder neues `simulation/engine.py`  
**Was:** WorkloadProfiler und CapacityCheck als eigene, komponierbare Stages statt Teil von
`rdc_rank()`; `DeploymentRecommendation`-Objekt als strukturierter Output statt Pareto-Liste.
**Grundlage:** `docs/phase3_simulation_concept.md` §3 (Datenflussbild), TASK-08.  
**Aufwand:** ~1 Tag

### TASK-01 · Prozessintegrationsmodell (D2-01) `Phase 2 Deliverable`
**Datei:** `docs/phase2_process_integration.md` (noch nicht vorhanden)  
**Was:** Beschreibt, wie CO₂-KPIs in den Software-Lifecycle integriert werden — welcher KPI an welchem Prozessschritt greift, welche Rolle verantwortlich ist, welche Entscheidungspunkte es gibt.  
**Grundlage:** `data/lifecycle_mapping.yaml` (19 KPI-Mappings), `data/green_gates.yaml` (Gates je KPI), Vorgehensvorschlag §4.2  
**Aufwand:** ~1 Tag  
**Output:** Markdown-Dokument, exportierbar über `build_exports.py`

### TASK-02 · KPI-to-Process-Mapping YAML (D2-03) `Phase 2 Deliverable`
**Datei:** `data/kpi_process_mapping.yaml` (noch nicht vorhanden)  
**Was:** Strukturiertes Datenmodell: welcher KPI ist an welchem Prozessschritt aktiv, welche Rolle ist owner, welcher Green Gate greift.  
**Grundlage:** `data/kpis.yaml`, `data/lifecycle_mapping.yaml`, `data/green_gates.yaml`  
**Format:** YAML analog zu `lifecycle_mapping.yaml`; ID-Schema: `MAP-P-001` etc.  
**Aufwand:** ~0.5 Tage  
**Output:** Neues YAML, Export über `build_exports.py` erweitern

### TASK-03 · Best Practices Dokument (D2-04) `Phase 2 Deliverable`
**Datei:** `docs/phase2_best_practices.md` (noch nicht vorhanden)  
**Was:** Erfolgsfaktoren, Barrieren, Mindest-Voraussetzungen für CO₂-KPI-Integration; strukturiert nach Erfahrungen aus Phase 1+2.  
**Grundlage:** `docs/phase2_instrumentation_backlog.md` (Klärungspunkte OC-01 bis OC-05), Gap-Analyse  
**Aufwand:** ~0.5 Tage  
**Output:** Markdown-Dokument

### TASK-04 · Design Principles Dokument (D2-02 ergänzen) `Phase 2 Deliverable`
**Datei:** `docs/phase2_design_principles.md` (noch nicht vorhanden)  
**Was:** Schriftliche Design-Prinzipien für Green / Sustainable DevOps — basierend auf dem EfficiencyScore-Modell und den Green Gates. Standalone-Dokument für DHL-Stakeholder.  
**Grundlage:** `data/green_gates.yaml`, `data/hardware_configs.yaml` (EfficiencyScore-Gewichte), `docs/phase3_simulation_concept.md`  
**Aufwand:** ~0.5 Tage

### TASK-05 · Simulation erweitern: mehr Stellvariablen `Enhancement`
**Datei:** `generators/simulation_runner.py`  
**Was:** `SCENARIO_AXES` um `avg_latency_s` und `quality_score` erweitern; optional: Sensitivitätsplot als ASCII-Tabelle.  
**Aufwand:** ~0.5 Tage  
**Wie:** `SCENARIO_AXES["avg_latency_s"] = [1.0, 5.0, 30.0]` eintragen und Kommentar aktualisieren.

### TASK-06 · `build_exports.py` um KPI-Process-Mapping-Export erweitern `Enhancement`
**Datei:** `generators/build_exports.py`  
**Was:** Wenn `data/kpi_process_mapping.yaml` (TASK-02) existiert, als Export `KPI_Process_Mapping.md` erzeugen.  
**Aufwand:** ~0.5 Tage

### TASK-07 · `embodied_co2_kg` befüllen `Data Quality`
**Datei:** `data/hardware_configs.yaml`  
**Was:** Für jede Tier-Konfiguration `embodied_co2_kg` aus Vendor-PCF-Datasheets oder Ecoinvent ergänzen. Hebt PRX-003 von `quality: medium` auf `quality: high`.  
**Quellen:** NVIDIA PCF-Reports (veröffentlicht für ausgewählte Produkte), Ecoinvent-Datenbank, Dell/HP Sustainability-Reports  
**Aufwand:** ~0.5–1 Tag je nach Datenverfügbarkeit

---

## Wartet auf DHL-Input — geblockt

| Task | Was gebraucht wird | Auswirkung |
|---|---|---|
| **Pilot A bestimmen** | Name + Beschreibung der CI/CD-Pipeline | Tier-0 T0-01 (Eco-CI einbauen) |
| **Pilot B bestimmen** | Name + Beschreibung des Run-Services | Tier-0 T0-02/T0-04 |
| **Rechenzentrum / Cloud-Region** | Standort des Pilots | Carbon Intensity Feed T0-03 |
| **APM-Lösung benennen** | Datadog / Dynatrace / Prometheus / OTel? | T0-04 Request-Zähler aktivieren |
| **Hardware-Inventar Pilot** | Welche Server / Cloud-Instanzen laufen für Pilot A+B? | HW-001 aus Proxy auf echte Daten heben |
| **RACI-Rollen besetzen** | 6 Rollen (KPI Owner, Steward, Boundary Curator, Data Quality, Release Approver, Audit Liaison) | GAP-004 schließen |
| **Green Gates bestätigen** | Schwellenwerte in `data/green_gates.yaml` prüfen / ersetzen | Ohne Abnahme bleiben Gates „KRALLMANN Default" |

---

## Abhängigkeitskette (vereinfacht)

```
DHL bestätigt Pilot-Scope (OC-01/02)
    │
    ├─► TASK-01 Prozessintegrationsmodell  (kein Blocker)
    ├─► TASK-02 KPI-Process-Mapping YAML   (kein Blocker)
    ├─► TASK-03 Best Practices             (kein Blocker)
    │
    └─► Tier-0 Instrumentation startet
            │
            └─► Tier-1 Instrumentation
                    │
                    └─► Phase 3: Dashboard, Live-Telemetrie, Green Gate Integration
```

---

## Definition of Done Phase 2

Phase 2 ist abgeschlossen, wenn:
- [ ] Alle 6 Deliverables (D2-01 bis D2-06) fertig und durch DHL reviewt
- [ ] Pilot-Scope entschieden (OC-01 bis OC-05)
- [ ] GAP-003 in Pilot-Scope operational (HW-001 liefert Zahlen)
- [ ] GAP-005 für Pilot-KPIs geschlossen (ISO-Mapping vollständig)
- [ ] `data/green_gates.yaml` von DHL abgenommen
- [ ] Mindestens ein Stakeholder-Review abgeschlossen

---

## Technische Kurzreferenz

Seit 2026-07-10 gibt es eine `pyproject.toml` (uv-verwaltet, additiv). Erststart:
`uv sync --extra dev`. Die bisherigen direkten Skriptaufrufe funktionieren unverändert weiter,
sofern `pyyaml`/`jsonschema` anderweitig verfügbar sind — empfohlen ist aber `uv run`:

```bash
# Einmalig: venv + Dependencies (inkl. adaptive_decision_kernel als editable Dependency)
uv sync --extra dev

# Tests
uv run pytest tests/ -q

# Validierung + alle Exports neu erzeugen
PYTHONUTF8=1 uv run python ci/validate_and_export.py

# Simulation: 192 Szenarien × 6 Infrastruktur-Tiers (816 Zeilen)
PYTHONUTF8=1 uv run python generators/simulation_runner.py

# Hardware-Modell direkt testen
PYTHONUTF8=1 uv run python generators/hardware_model.py

# Pareto-Frontier + Sensitivität (neu, TASK-08)
PYTHONUTF8=1 uv run python generators/rdc_pareto.py
```

**Wichtig:** `exports/` ist gitignored. Exports immer lokal regenerieren, nie committen.  
**Python-Version:** 3.12+ (siehe `pyproject.toml`). Dependencies: `pyyaml`, `jsonschema`,
`adaptive-decision-kernel` (editable, Pfad `../adaptive_decision_kernel`).

---

## Verweise

| Thema | Datei |
|---|---|
| Vollständige Roadmap | `ROADMAP.md` |
| KPI-Katalog (SSOT) | `data/kpis.yaml` |
| Gaps & Proxies | `data/assumptions_proxies.yaml` |
| Green Gates | `data/green_gates.yaml` |
| Hardware-Tiers | `data/hardware_configs.yaml` |
| Gap-Analyse RDC | `docs/phase2_rdc_gap_analysis.md` |
| Instrumentation Backlog | `docs/phase2_instrumentation_backlog.md` |
| Simulation Konzept Phase 3 | `docs/phase3_simulation_concept.md` |
| Pareto/Sensitivität (TASK-08) + Cross-Repo-Vorhaben | `docs/enterprise_simulation_roadmap.md` |
| Phase-1-Entscheidungen | `docs/decision_packs/phase1_initial/decisions.yaml` |
| Projektangebote | `OneDrive 00_Projektmanagement/03_Projektangebote/` |
