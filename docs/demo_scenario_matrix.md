# Demo Scenario Coverage Matrix

**Zweck:** Systematische Einordnung der Demo-Szenarien (`data/demo_scenarios.yaml`), um
Abdeckung der Datenmodell-Dimensionen messbar zu machen und bewusst offene Zellen sichtbar
zu machen — Prinzip übertragen aus `economic_intelligence_engine/docs/usecase_matrix.md`
(dortiges A×B-Raster über analytische Funktion × Fachdomäne), hier angewendet auf
Funktionstyp × Volumenklasse für Infrastruktur-Entscheidungsszenarien.

`generators/demo_scenarios.py::coverage_summary()` prüft maschinell, dass jede in diesem
Dokument referenzierte Szenario-ID auch tatsächlich in `data/demo_scenarios.yaml` existiert
und umgekehrt (Drift-Guard, getestet in `tests/test_demo_scenarios.py`) — analog zum
`coverage_report.py`/`test_coverage_report.py`-Paar im Referenzrepo.

## Achsen

**Achse A — Funktionstyp** (wie wird das Modell in einem DHL-artigen Betrieb eingesetzt):
- **K1** Kundeninteraktion Echtzeit (Chat, Ticket-Routing)
- **K2** Bilderkennung/Sortierung Echtzeit (Computer Vision am Fließband/Hub)
- **K3** Batch-Analytics/Prognose (Forecasting, Optimierung, kein Live-Traffic)
- **K4** Vorausschauende Wartung/Anomalieerkennung (Sensor-/Log-Batches)

**Achse B — Volumenklasse** (Requests/Monat, an `SCENARIO_AXES` in
`generators/simulation_runner.py` angelehnt):
- **V1** niedrig (~1.000/Monat)
- **V2** mittel (~10.000/Monat)
- **V3** hoch (~100.000/Monat)
- **V4** sehr hoch (~1.000.000+/Monat)

## Matrix (8 von 16 Zellen belegt)

| Funktion ↓ \ Volumen → | V1 niedrig | V2 mittel | V3 hoch | V4 sehr hoch |
|---|---|---|---|---|
| **K1 Kundeninteraktion Echtzeit** | · | █ DEMO-01 | · | █ DEMO-02 |
| **K2 Bilderkennung/Sortierung Echtzeit** | · | · | █ DEMO-03 | █ DEMO-04 |
| **K3 Batch-Analytics/Prognose** | █ DEMO-05 | █ DEMO-06 | · | · |
| **K4 Vorausschauende Wartung/Anomalie** | █ DEMO-07 | █ DEMO-08 | · | · |

`█` = belegt (Szenario existiert und ist getestet). `·` = bewusst offen (siehe unten).

## Bewusst offene Zellen (kein Bug, dokumentierte Begründung)

- **K1×V1, K1×V3** — Kundeninteraktions-Services (Chat/Ticket-Routing) laufen bei einem
  Unternehmen der Größenordnung DHL praktisch nie dauerhaft im niedrigen Volumenbereich;
  V2/V4 decken die relevante Bandbreite (Regelbetrieb bis Peak) bereits ab, V3 wäre eine
  redundante Zwischenstufe ohne zusätzlichen Erkenntniswert für die Demo.
- **K2×V1, K2×V2** — Bilderkennung an einem Sortier-Fließband ist an den physischen
  Anlagenbetrieb gekoppelt und läuft strukturell immer im Hoch-/Sehr-Hoch-Volumenbereich;
  ein Fließband "mit niedrigem Volumen" zu betreiben ist kein reales Szenario.
- **K3×V3, K3×V4** — Batch-Analytics-Jobs (Prognose, Optimierung) sind Läufe, kein
  Anfragenstrom; "100.000+ Läufe/Monat" bildet kein reales Nutzungsmuster ab (degenerierte
  Zelle im Sinne des Referenzrepos: der Rasterpunkt existiert formal, ist aber fachlich
  nicht sinnvoll erreichbar).
- **K4×V3, K4×V4** — Wartungs-/Anomalieerkennung auf Sensor- oder Log-Batches skaliert
  nicht auf Hochvolumen-Requests; die Auswertefrequenz ist durch Sensor-/Log-Zyklen
  begrenzt, nicht durch Nutzeranfragen.

## Szenarien außerhalb der Matrix (Robustheit/Governance)

Analog zum robustness/adversarial-Testfall im Referenzrepo (dort die einzige Ausnahme vom
reinen Matrix-Prinzip): zwei Szenarien decken bewusst keine Funktions×Volumen-Zelle ab,
sondern prüfen Modellverhalten an Extremwerten bzw. die Ehrlichkeit der Empfehlungslogik:

- **DEMO-09** "Peak-Stresstest: Chatbot × 5 Volumen" — 5 Mio. Requests/Monat, oberhalb des
  regulären `SCENARIO_AXES`-Bereichs (max. 1 Mio.). Prüft, ob Amortisierungseffekt und
  Empfehlung auch am oberen Rand plausibel bleiben.
- **DEMO-10** "Worst-Case: Altbestand ohne Ökostrom" — bewusst ungünstige Parameterwahl.
  Prüft, dass `generators/decision_support.py::recommend_tier()` einen durchgängig
  roten/kritischen Fall auch als solchen ausweist, statt die "am wenigsten schlechte"
  Option unkommentiert als Erfolg darzustellen.

## Bezug zum Datenmodell

Jedes Szenario setzt konkrete Werte für alle sechs Stellvariablen aus
`generators/simulation_runner.py::SCENARIO_AXES` (`min_vram_gb`, `requests_per_month`,
`pv_share`, `grid_ef_gco2e_per_kwh`, `avg_latency_s`, `quality_score`) plus
`business_value_score` — die Matrix stellt damit sicher, dass die Demo-Bibliothek nicht
nur einen einzelnen Referenz-Workload zeigt (wie bisher `dashboard/app.py`s feste
`model_size_b=70`-Vorgabe), sondern das Datenmodell entlang realistisch unterscheidbarer
Geschäftsfälle sichtbar macht.
