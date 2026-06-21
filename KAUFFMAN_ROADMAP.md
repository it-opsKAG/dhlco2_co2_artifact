# Kauffman Integration Roadmap
**KRS: 52/100 | Priority: Mittel | Stand: 2026-06-21**

## KRS-Ziele
| Dimension | Aktuell | Nächstes Ziel | Delta | Aktion |
|---|---|---|---|---|
| D2 Constraint Closure | 7/10 | 8/10 | +1 | GreenGateDecision als CI-Blocker: gate_failed → Pipeline-Stop |
| D1 Self-Organization | 3/10 | 5/10 | +2 | Agent-driven NK-Landscape Search ersetzt kartesischen Sweep |
| D3 Autocatalytic Pot. | 5/10 | 7/10 | +2 | simulation_runner.py als adaptive_agent_os Tool-Wrapper exportieren |
| D4 Adjacent Possible | 5/10 | 6/10 | +1 | EmissionFactorProfile als erweiterbare Provider-Schnittstelle dokumentieren |
| D5 NK-Complexity | 6/10 | 7/10 | +1 | exports/ aus .gitignore entfernen; Artefakte automatisch verfügbar machen |
| D6 Energy Efficiency | 6/10 | 8/10 | +2 | Electricity Maps API ersetzt statischen UBA-Emissionsfaktor |
| D7 Phase Transitions | 5/10 | 7/10 | +2 | OTel/APScheduler für maschinell erzwingbare Phasenübergänge integrieren |

**KRS aktuell: 52 | Nächstes Ziel: 61 | Ceiling: 70**

## Kauffman-These
DHLCO2 operationalisiert Constraint Closure auf Messpunkt-Ebene: SCI-Formel, Green-Gate-Policy und `rdc_rank()`-Budget-Filter bilden eine geschlossene Constraint-Topologie — KRS niedrig by design, deterministisches Beratungsartefakt, keine Selbstorganisation vorgesehen.

## Implementiert
- [x] Kein Handlungsbedarf (intentional — existing system is the target state for v1)

## Uebersprungen
- Keine bestehende Funktionalitaet veraendert — deterministisches Artefakt, Ergaenzungen nur in KAUFFMAN_ROADMAP.md dokumentiert.

## Geplant (L-Items, naechste Session)
- [ ] Electricity Maps API (Tier T1-03): statischen UBA-Emissionsfaktor durch Echtzeit-Regional-Carbon-Intensitaet ersetzen — Aufwand: L
- [ ] OTel/APScheduler (T1-05): GreenGateDecision-Records in CI/CD pipeline einspeisen, maschinell erzwingbare Phasenuebergaenge ermoeglichen — Aufwand: L
- [ ] `simulation_runner.py` als Tool-Wrapper fuer adaptive_agent_os: Szenario-Ergebnisse als Agent-Trainingssignal exportieren — Aufwand: L

## Visionaer (XL)
- [ ] Agent-driven NK-landscape search als Ersatz fuer kartesischen Szenario-Sweep (192 Szenarien → adaptive Exploration)
- [ ] Vollstaendiger CO2-SSOT als adaptive_decision_kernel Datenquelle (Live-Feed statt statischer YAML-Snapshots)

## Cross-Repo Verbindungen
- economic_intelligence_engine: CO2-Datenquelle — Simulationsergebnisse als Wirtschaftsindikator einspeisen
- adaptive_decision_kernel: SSOT-Daten — Green-Gate-Entscheidungen als Constraint-Input
- adaptive_agent_os: simulation_runner.py als aufrufbares Tool, Szenario-Outputs als Trainingssignal
