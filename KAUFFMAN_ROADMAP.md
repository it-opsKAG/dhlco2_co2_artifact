# Kauffman Integration Roadmap
**KRS: 52/100 | Priority: Mittel | Stand: 2026-06-21**

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
