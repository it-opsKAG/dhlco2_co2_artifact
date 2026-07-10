# Enterprise/Organization Simulation — Roadmap

## Kontext

Ziel: ein Unternehmen/eine Organisation als komplexes, simulierbares System modellieren,
aus zwei Blickwinkeln:

- **Sicht 1 (Makro):** Steuergrößen (Kosten, CO2/Energie, Risiko, später Umsatz) werden unter
  Constraints optimiert/simuliert.
- **Sicht 2 (Mikro):** Mitarbeiter/Akteure als Prozessknoten mit Input-Abhängigkeiten (Kontext,
  Dokumentation, Wissen, Artefakte, Input von anderen Akteuren).

Ausgangspunkt war eine Repo-Inventur-Analyse (AFOS-Ollama-Lauf, 2026-07-10), die durch
Token-Budget-Überschreitung abgebrochen wurde und dadurch mehrere ungenaue Angaben enthielt.
Eine vollständige Verifikation (5 parallele Explore-Agents + direkte Code-Lektüre) ergab: die
Software-Bausteine für Sicht 1 sind größtenteils vorhanden und produktionsreif; Sicht 2 existiert
bisher nur theoretisch (InProKI/NeuroShift-Framework im Vault) bzw. in einer sehr schlanken Form
(dieses Dokument selbst, siehe `docs/phase2_process_integration_model.md`).

**Nutzer-Entscheidungen (2026-07-10):**
- Erster Pilot: DHL/DHLCO2 ausbauen — den RDC-Operator aus `docs/phase3_simulation_concept.md`
  von Phase-2-Stub zu echter Phase-3-Simulation bringen.
- Sicht-2-Tiefe: schlank starten (echte Input-Slots statt voller InProKI-NEA/NKMM-Theorie).

## Architekturentscheidung

Kein neues Mega-Repo. Die bestehende Kernel/Host/Pack-Trennung
(`adaptive_decision_kernel` ↔ `adaptive_decision_simulator`, siehe
`adaptive_decision_simulator/docs/pack_host_architecture.md`) ist bereits die richtige
Architektur. Der RDC-Operator (`RDC(x) = argmax_c Utility(c,w)` unter Constraints) ist schon
fast domänenneutral formuliert — die generische Optimierungs-Maschinerie (Pareto-Frontier,
Sensitivitätsanalyse) lebt im **Kernel** (`adaptive_decision_kernel`), die DHL-spezifischen
Modelle (Cost/Energy/CO2Model) bleiben in diesem Repo.

## Run-Plan

| Run | Titel | Status |
|---|---|---|
| 1 | Foundation: Pareto/Sensitivität im Kernel + erster DHL-Beweis | **DONE 2026-07-10** |
| 2 | Volle Phase-3-SimulationEngine (WorkloadProfiler/CapacityCheck als eigene Stages, DeploymentRecommendation) | offen |
| 3 | Unsicherheitsbänder / Monte-Carlo-Kalibrierung (embodied_co2 ±50%, η_parallel ±10-20%) | offen |
| 4 | Sicht-2-Grundgerüst: Actor/InputSlot/ProcessStep-Contracts im Kernel (schlank) | offen |
| 5 | Sicht1↔Sicht2-Brücke: Akteurs-Constraints in der RDC-Utility | offen |
| 6 | Pack-Integration: `dhl_monitoring`-Pack bekommt `simulate`-Mode | offen |
| 7 | Zweiter Pilot (Generalitätsbeweis): neuer Pack, domänenfremder Fall | offen |
| 8 | Ökonomische Kalibrierung für Pilot 2 (economic_intelligence_engine-Adapter) | offen |
| 9 | AAOS-Process-Runtime-Anbindung | offen |
| 10 | KRS/Telemetry (platform_core) | offen |
| 11 | Cockpit-Visualisierung (AAOS apps/web: Actor-Graph + Pareto-Frontier) | offen |
| 12 | Härtung + Dissertations-/InProKI-Linkage | offen |

## Run 1 — was tatsächlich gebaut wurde (Beweis)

- `adaptive_decision_kernel/src/adaptive_decision_kernel/optimization.py` — neue,
  domänenneutrale Contracts `Dimension`/`Candidate` + `pareto_frontier()` +
  `sensitivity_ratios()`. 7 Unit-Tests, alle grün (`tests/test_optimization.py`).
- `dhlco2_co2_artifact/pyproject.toml` (neu) — macht dieses Repo erstmals `uv`-verwaltbar
  (editable Dependency auf `adaptive-decision-kernel`), **ohne** die bestehende Skript-Struktur
  (`generators/*.py`, `ci/validate_and_export.py`) umzubauen. Bestehende CI-Pipeline lief
  danach unverändert grün (`uv run python ci/validate_and_export.py` → `validate_and_export: ok`).
- `generators/rdc_pareto.py` (neu) — baut aus `hardware_model.py::rdc_rank()`'s bestehenden
  Metriken (CO2/Request, EUR/Request, EfficiencyScore) echte Pareto-Candidates und reduziert auf
  die Pareto-Front, statt nur nach einer einzigen Dimension zu sortieren. Plus
  `co2_sensitivity_to_requests_per_month()` — echte Δco2/ΔStellvariable-Analyse.
- 4 Integrationstests (`tests/test_rdc_pareto.py`), alle grün. Realer Demo-Lauf gegen die
  echten `data/hardware_configs.yaml`-Daten: von 4 machbaren Configs sind 2 Pareto-optimal;
  CO2/Request sinkt mit steigendem Request-Volumen (Amortisierungseffekt), Sensitivität
  nimmt erwartungsgemäß mit dem Volumen ab.
- Damit ist der in `docs/phase3_simulation_concept.md` §3 beschriebene ParetoOptimizer-Schritt
  erstmals real (nicht mehr nur konzipiert) — der `hardware_model.py::rdc_rank()`-Stub bleibt
  unverändert und rückwärtskompatibel; `rdc_pareto.py` ist eine additive Erweiterung.

## Verwandte Dokumente

- `docs/phase3_simulation_concept.md` — RDC-Operator, Stellvariablen, Erweiterungspfad Phase 3/4
- `docs/phase2_process_integration_model.md` — bestehendes, schlankes Sicht-2-Muster
- `adaptive_decision_simulator/docs/pack_host_architecture.md` — Kernel/Host/Pack-Vertrag
