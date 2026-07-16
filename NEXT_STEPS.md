# Next Steps — DHLCO2 CO₂-Artefakt

**Letzte Aktualisierung:** 2026-07-16  
**Phase:** 2 (In Bearbeitung, ~85%; alle 6 Dokument-Deliverables D2-01 bis D2-06 fertig, offen: DHL-Review + Pilot-Scope OC-01..05); Phase-3-Vorstufe (Pareto/Sensitivität, interaktives Dashboard, Entscheidungsunterstützung) zusätzlich gestartet, siehe TASK-08, TASK-11, TASK-15  
**Vollständige Roadmap:** `ROADMAP.md` · **Cross-Repo-Vorhaben:** `docs/enterprise_simulation_roadmap.md`

Dieses Dokument ist der Einstiegspunkt für die nächste Arbeitssitzung.  
Kein Kontextwissen nötig — alles Nötige steht hier oder ist verlinkt.

---

## Erledigt (nicht mehr TODO, hier als Kontext für den nächsten Schritt)

### TASK-01 · Prozessintegrationsmodell (D2-01) `Done — bereits 2026-06-29 vorhanden`
**Datei:** `docs/phase2_process_integration_model.md` (bestehend, Statustabelle in `ROADMAP.md` war veraltet und wurde 2026-07-14 korrigiert). Inhalt erfüllt den TASK-01-Zweck vollständig (Lifecycle-Schritte × KPI-Gruppen, Integrationsprinzipien, Rollen).

### TASK-02 · KPI-to-Process-Mapping YAML (D2-03) `Done 2026-07-14`
**Dateien:** `data/kpi_process_mapping.yaml` (neu, MAP-P-001..019, aus der bestehenden Prosa-Tabelle `docs/phase2_kpi_to_process_mapping.md` transkribiert), `generators/build_exports.py` (Export `KPI_Process_Mapping.md` ergänzt, siehe TASK-06).

### TASK-03 · Best Practices Dokument (D2-04) `Done 2026-07-14`
**Datei:** `docs/phase2_best_practices.md` (neu) — Erfolgsfaktoren, Barrieren, Mindest-Voraussetzungen (Tier-0-Checkliste), übertragbare Lektionen.

### TASK-04 · Design Principles Dokument (D2-02 ergänzt) `Done 2026-07-14`
**Datei:** `docs/phase2_design_principles.md` (neu) — 7 Prinzipien inkl. EfficiencyScore-Gewichtstabelle und Zusammenspiel mit Green Gates.

### TASK-06 · `build_exports.py` um KPI-Process-Mapping-Export erweitert `Done 2026-07-14`
**Datei:** `generators/build_exports.py` — rendert `exports/KPI_Process_Mapping.md`, wenn `data/kpi_process_mapping.yaml` existiert. Zusätzlich: `_group_counts_summary()` um Gruppe „Hardware & Embodied" ergänzt (fehlte bisher in der Gruppen-Reihenfolge von `Framework_Overview.md`).

### TASK-10 · Evidence Ledger für Simulationsläufe (TD-05 schließen) `Done 2026-07-14`
**Dateien:** `generators/evidence_ledger.py` (neu), `evidence/simulation_runs.jsonl` + `evidence/SIMULATION_EVIDENCE_LEDGER.md` (neu, committed).
**Was:** Jeder Simulationslauf bekommt eine RUN-ID (`RUN-{YYYYMMDD}T{HHMMSS}Z-SIM-fullsweep`, gleiches Schema wie die Dissertations-Validation-Matrix), den Git-Commit-Hash und SHA-256-Hashes der Output-Dateien. Erster echter Lauf: `RUN-20260713T221421Z-SIM-fullsweep` — bestätigt 192 Szenarien / 816 Zeilen exakt wie im Statusupdate-Deck behauptet.
**Live-Grid-Carbon (zusätzlich, kein NEXT_STEPS-Task, siehe `generators/live_grid_carbon.py`):** Live-Abruf des echten deutschen Netz-Emissionsfaktors über die tokenlose energy-charts.info-API (Fraunhofer ISE) — ergänzt den bisher rein statischen UBA-2024-Wert um einen echten Live-Datenpunkt für Demos.

### TASK-11 · Interaktives Streamlit-Dashboard `Done 2026-07-15, erweitert 2026-07-16 (TASK-15)`
**Dateien:** `dashboard/app.py`, `dashboard/data_helpers.py`, `dashboard/README.md` (neu).
**Was:** Lokale Demo-App (6 Tabs: KPI-Katalog & Green Gates, Hardware-Vergleich, Pareto-Frontier, Sensitivität, Live-Kontext, Auditability) — läuft auf dem bestehenden, getesteten Modell (`hardware_model.py`, `rdc_pareto.py`, `live_grid_carbon.py`, `evidence_ledger.py`), keine Mock-Daten. Start: `uv sync --extra dashboard && uv run streamlit run dashboard/app.py`.
**Gefundener Nebenbefund:** `data/green_gates.yaml` hat kein Gate für SCI-001/SCI-002 (aggregierte Kennzahlen ohne universellen Schwellenwert) — bewusst nicht nachgerüstet, im Dashboard transparent als "kein Gate" markiert statt einen falschen Präzisionsanschein zu erzeugen.
**Siehe TASK-15 für die 2026-07-16-Erweiterung** (Entscheidungsfrage zuerst, benannte Szenarien, aggregierter Gate-Status, Hebel-Ranking, Tier-Empfehlung).

### TASK-15 · Entscheidungsunterstützung: benannte Szenarien, aggregierter Gate-Status, Hebel-Ranking, Tier-Empfehlung `Done 2026-07-16`
**Auslöser:** Stakeholder-Feedback zur Statusupdate-Präsentation — Demonstrator sollte nicht mit dem KPI-Katalog starten, sondern mit der Entscheidungsfrage "Welche Infrastrukturkonfiguration ist unter CO2-, Kosten- und Effizienzgesichtspunkten die beste?" und einer Empfehlung inkl. CO2/Kosten/Green-Gate/Datenqualität enden.
**Neue Dateien:**
- `generators/green_gates.py` — Gate-Zone-Klassifikation aus `dashboard/data_helpers.py` extrahiert (reine Logik, keine Streamlit-Abhängigkeit), damit `decision_support.py` sie nutzen kann, ohne dass `generators/` von `dashboard/` abhängt. `data_helpers.py` re-exportiert dieselben Namen — keine Breaking Changes für bestehende Importe.
- `generators/decision_support.py` — die "letzte Verdichtungsschicht":
  - `aggregate_gate_status()`: worst-of-Aggregation über RUN-001/RUN-002/RUN-004 (HW-001/HW-002 bewusst ausgeschlossen, da `threshold_basis: tbd`).
  - `rank_co2_levers()` / `rank_cost_levers()`: One-at-a-time-Headroom-Analyse je Stellvariable (Δ bei fixierter Hardware), verallgemeinert aus der bestehenden `co2_sensitivity_to_requests_per_month()`-Logik in `rdc_pareto.py`. Bewusst zwei getrennte Rankings statt eines künstlichen Gesamt-Scores — `quality_score` wirkt nachweislich nur auf Kosten, nicht auf CO2; `grid_ef`/`pv_share` nur auf CO2, nicht auf Kosten. **Nachschärfung 2026-07-16 (Audit):** Erste Fassung maß die Spannweite zwischen festen Worst/Best-Grenzen — dadurch zeigte jedes Szenario denselben Top-Hebel („Nutzungsvolumen, Δ 7.98") selbst wenn es bereits am Volumen-Bestwert lag (DEMO-02/04/09). Jetzt wird das **verbleibende Potenzial ab den aktuellen Szenario-Werten** zum Modell-Bestwert gemessen (geklemmt auf ≥0); Regressionstests `test_rank_co2_levers_is_scenario_sensitive` und `test_rank_co2_levers_clamps_beyond_best_values_to_zero` sichern das ab. Ergebnis: Hochvolumen-Echtzeit-Szenarien zeigen jetzt korrekt Strommix/PV als stärksten verbleibenden Hebel, Niedrigvolumen-Szenarien Konsolidierung/Volumen.
  - `recommend_tier()`: wählt Pareto-optimale + gate-konforme Konfiguration, Tie-Break über den bestehenden EfficiencyScore, generiert einen auditierbaren Beispielsatz ("Tier X ist für [Szenario] die empfohlene Option: ..."). Fällt bei durchgängig rotem Gate ehrlich auf die am wenigsten kritische Option zurück (`all_candidates_red`-Flag) statt das Problem zu verschleiern.
- `data/demo_scenarios.yaml` + `generators/demo_scenarios.py` — 10 benannte, illustrative DHL-Beispielszenarien (Chatbot, Sortierzentrum-OCR, Schadenserkennung, Bedarfsprognose, Routenoptimierung, Predictive Maintenance, IT-Anomalieerkennung + 2 Robustheits-/Governance-Edge-Cases), systematisch über eine Funktionstyp×Volumenklasse-Matrix eingeordnet (siehe `docs/demo_scenario_matrix.md`, Prinzip von `economic_intelligence_engine/docs/usecase_matrix.md` übernommen). Maschineller Drift-Guard prüft, dass Matrix-Doku und YAML in Sync bleiben.
**Datenmodell-Erweiterung (rückwärtskompatibel):** `WorkloadProfile.avg_latency_s` (Default 5.0, wie bisher) ist jetzt ein echtes, im interaktiven Dashboard einstellbares Feld — vorher war die Latenz nur im Batch-Sweep (`simulation_runner.py`) variabel, im Dashboard immer fest auf 5s verdrahtet. Neu: `run002_energy_wh_per_request()` (RUN-002 direkt statt aus CO2 zurückgerechnet) und `run004_energy_proportionality_ratio()` (Proxy aus Idle/Load-TDP, da echte Auslastungstelemetrie an OC-01..05 blockiert ist).
**Dashboard-Umbau:** `dashboard/app.py` führt jetzt mit der Entscheidungsfrage + einer immer sichtbaren Ergebnisbox (Empfehlung, CO2, Kosten, Green-Gate, Datenqualität); Sidebar startet mit einem Szenario-Dropdown (Default: DEMO-02 Chatbot) statt nackten Reglern, alle Stellvariablen bleiben frei editierbar; neuer erster Tab "Entscheidung & Begründung" (Rationale, Gate-Aufschlüsselung, Hebel-Ranking, Pilotfähigkeit-Hinweis); KPI-Katalog auf Tab-Position 5 verschoben (nicht mehr Startpunkt); Netz-EF-Regler um Live-Quellen-Auswahl (energy-charts.info/ENTSO-E) erweitert, die direkt in dieselbe Berechnung einfließt statt nur als Info-Tab.
**Ehrlicher Befund beim Testen (kein Bug, Kalibrierungs-Hinweis für DHL):** RUN-001s absoluter Schwellenwert (≤0.10 gCO2e/Transaktion, kalibriert auf "typischen Web-Service-Footprint") lässt GPU-Batch-Workloads mit niedrigem Volumen (z.B. 1.000 Requests/Monat) praktisch immer als "rot" erscheinen, weil die Embodied-CO2-Amortisierung pro Request bei so wenig Traffic hoch bleibt — unabhängig von der Hardware-Wahl. Von den 10 Demo-Szenarien sind 4 grün (hochvolumige Echtzeit-Services) und 6 rot (niedrig-/mittelvolumige Batch-/Klassifikationsworkloads). Das ist ein reales Kalibrierungsthema von RUN-001 (`threshold_basis: krallmann_default`, laut eigenem `sensitivity_note` "illustrativ bis zur Pilot-Baseline"), keine Fehlfunktion — die Empfehlungs-Engine zeigt es transparent an, verschweigt es nicht.
**Tests:** `tests/test_hardware_model.py`, `tests/test_decision_support.py`, `tests/test_demo_scenarios.py` (neu, 49 neue Tests), `tests/test_dashboard_app.py` angepasst (KPI-Katalog nicht mehr Tab 1). Gesamte Suite: 79 passed (2 live-marked deselected wie zuvor). Batch-Sweep (1728/7344), `hardware_model.py`-CLI und `ci/validate_and_export.py` als Regressionstest gegen die Datenmodelländerung erneut grün gelaufen.
**Für nächste Session:** Business-Flags unverändert offen (Scope-Lücke, fehlende 23.-Juni-Mail, OC-01..05) — reine Kommunikation, kein Repo-Task. Die RUN-001-Kalibrierungsfrage (siehe oben) eignet sich als konkreter Diskussionspunkt für den nächsten DHL-Workshop.

### TASK-16 · Dokumentierte offene Verbesserungen (Backlog, kein Blocker für die Demo) `Offen`
Beim Architektur-/Verhaltens-Audit 2026-07-16 identifiziert und bewusst NICHT im Demo-Sprint umgesetzt — jeweils mit Begründung, warum verschiebbar:

1. **`efficiency_score()` ist workload-/emissionsfaktor-blind** (`generators/hardware_model.py`): Die Funktion bewertet nur statische Hardware-Eigenschaften (VRAM/EUR, VRAM/W, Reife, Risiko). Workload-Sensitivität entsteht in der Empfehlung derzeit über den Umweg Pareto-Zugehörigkeit + Gate-Konformität (beide hängen real von Workload/EF ab) — der Tie-Break bleibt aber statisch. Sinnvolle Erweiterung: Score-Komponenten für Auslastungsgrad/Energiemix, ODER bewusst so lassen und als „Hardware-Grundgüte" dokumentieren. Gehört fachlich zu TASK-09 (volle SimulationEngine mit `DeploymentRecommendation`).
2. **RUN-001-Schwellenwert-Kalibrierung** (`data/green_gates.yaml`): ≤0.10 gCO2e/Transaktion ist auf typische Web-Services kalibriert; GPU-Workloads mit <10k Requests/Monat sind dadurch strukturell rot (Embodied-Amortisierung), unabhängig von der Hardware-Wahl. Kein Code-Task — Workshop-Frage an DHL: volumen- oder workload-klassenabhängige Gates?
3. **RUN-004-Proxy bindet nie** (`run004_energy_proportionality_ratio`): Alle 7 Tiers liegen bei 0.73–0.86 (Gate grün ≥0.70) — der KPI nimmt an der Gate-Aggregation teil, diskriminiert aber mit dem aktuellen Katalog nicht. Erwartbar für einen statischen Idle/Load-TDP-Proxy; echte Diskriminierung kommt erst mit gemessener Auslastung (blockiert an OC-01..05). Transparent halten, nicht künstlich verschärfen.
4. **Performance-Politur (optional):** `rdc_rank()` lädt `hardware_configs.yaml` bei jedem Aufruf neu; das Hebel-Ranking macht ~6 `rdc_rank()`-Aufrufe pro Rerun. Bei aktueller Katalataloggröße einstellig Millisekunden — für die lokale Demo irrelevant, bei echtem Multi-User-Betrieb `@st.cache_data`/Modul-Cache nachrüsten.
5. **`sys.path`-Importmuster statt Paketstruktur:** Bewusste Repo-Konvention (flache `generators/`-Skripte, `package = false` in `pyproject.toml`), funktioniert und ist getestet — bei Wachstum auf ein installierbares Paket mit `src/`-Layout umstellbar, dann entfallen die Pfad-Hacks in `dashboard/`, `tests/conftest.py` und den Generator-Modulen.

### TASK-07 · `embodied_co2_kg` befüllen `Done 2026-07-15`
**Datei:** `data/hardware_configs.yaml`. Statt Vendor-PCF (nicht verfügbar ohne DHL-Hardware-Inventar) wurde die **Boavizta-API** (`api.boavizta.org`, frei, offen, Bottom-up-LCA-Methodik, kein Token) live abgefragt: 4 von 7 Tiers direkt mit realen GPU-Referenzwerten befüllt (NVIDIA L4 24GB=113.6 kg, RTX A4500 20GB=141.4 kg, A100 PCIe 40GB=275.7 kg, H100 SXM 80GB=575.2 kg), 2 Tiers linear zwischen zwei echten Referenzpunkten interpoliert (klar als `boavizta_interpolated` gekennzeichnet). Cloud-Referenz-Tier bleibt bewusst Proxy (Provider-Scope-3-Grenze, von Ranking ausgeschlossen). PRX-003 entsprechend dokumentiert.

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

### TASK-05 · Simulation erweitern: mehr Stellvariablen `Done 2026-07-15`
**Datei:** `generators/simulation_runner.py`. `SCENARIO_AXES` um `avg_latency_s` ([1.0, 5.0, 30.0] s) und `quality_score` ([0.7, 0.85, 1.0]) erweitert — beide fließen jetzt tatsächlich in die Berechnung ein (vorher als Modul-Konstanten fixiert): `avg_latency_s` treibt `run_co2_per_request`, `quality_score` treibt neu ergänztes `cost_useful_outcome_eur` je Zeile. Szenarienzahl: 192 → 1728 (×9), Ergebniszeilen: 816 → 7344. Neuer Evidence-Ledger-Lauf: `RUN-20260714T210542Z-SIM-task05-more-stellvariablen`.

### TASK-12 · ENTSO-E-Connector (echte EU-Netzdaten) `Done + live verifiziert 2026-07-15`
**Datei:** `generators/entsoe_grid_carbon.py` (neu). Details, Zugriffsablauf und Mehrwert: `docs/phase3_data_source_roadmap.md` §1.
**Was:** Erzeugung nach Energieträger (documentType A75) von der offiziellen ENTSO-E Transparency Platform abrufen, per eigener Emissionsfaktor-Tabelle in einen CO2-Faktor umrechnen — ersetzt/ergänzt energy-charts.info um eine regulatorisch-autoritative, EU-weite Quelle.
**Ergebnis erster echter Lauf:** DE_LU, Fenster 2026-07-15T12:30–14:30 UTC, gewichteter CO2-Faktor 169–172 gCO2e/kWh (dominant: Solar), keine unmapped PSR-Codes. Live-Unit-Test (`test_fetch_generation_mix_smoke`, `-m live`) grün gegen die echte API. Drei-Wege-Vergleich zum selben Zeitpunkt: ENTSO-E 169–172, energy-charts.info 197.5, statischer UBA-2024-Wert 485 gCO2e/kWh — beide Live-Werte plausibel konsistent und deutlich unter dem Jahresdurchschnitt (Solarspitze im Juli-Mittag). Zusätzlich 10 weitere Bidding-Zonen (AT, BE, NL, FR, PL, CH, IT_NORD, ES, CZ, DK_1) ergänzt und einzeln live verifiziert.
**Aufwand:** ~0.5 Tag Code + Verifikation, wie geplant.

### TASK-13 · Eco-CI GitHub-Actions-Workflow (echte CI-Energiemessung) `Done + live verifiziert 2026-07-14`
**Datei:** `.github/workflows/energy-ci.yml` (neu — erste GitHub Actions CI für dieses Repo). Details + echte Messwerte: `docs/phase3_data_source_roadmap.md` §2.
**Was:** Misst echten Energieverbrauch (Joule, CPU-Auslastung, Watt) für den bestehenden `pytest`-Lauf via `green-coding-solutions/eco-ci-energy-estimation`. Kein Token nötig (globaler Default-CO2-Wert ohne Electricity-Maps-Key).
**Ergebnis erster echter Lauf:** SCI = 0.006042 gCO2eq/Pipeline-Lauf, 29.83 Joule, 21.82% Ø CPU — erster real gemessener (nicht simulierter) BLD-001-Wert des Projekts.

### TASK-14 · Cloud-Provider-Carbon-Tools anbinden `Offener Punkt, kein Code-Task`
**Details:** `docs/phase3_data_source_roadmap.md` §3. AWS Customer Carbon Footprint Tool / Google Cloud Carbon Footprint Export / Microsoft Azure Carbon Optimizer — sobald Cloud-Anbieter des Piloten bekannt ist (OC-01/OC-04), reine Zugriffsfrage (Lesezugriff Billing-Konto), kein Entwicklungsaufwand auf unserer Seite. Für Freitag als "nächster Schritt, sobald ihr uns Zugriff gebt" positioniert.

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

# Simulation: 1728 Szenarien × bis zu 6 Infrastruktur-Tiers (7344 Zeilen, seit TASK-05)
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
| Datenquellen-Roadmap (TASK-12/13/14) | `docs/phase3_data_source_roadmap.md` |
| Interaktives Dashboard (TASK-11) | `dashboard/README.md` |
| Phase-1-Entscheidungen | `docs/decision_packs/phase1_initial/decisions.yaml` |
| Projektangebote | `OneDrive 00_Projektmanagement/03_Projektangebote/` |
