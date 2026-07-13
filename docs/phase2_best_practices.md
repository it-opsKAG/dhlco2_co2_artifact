# Phase 2 Best Practices

**Datum:** 2026-07-14
**Status:** Phase-2-Deliverable (D2-04)
**Grundlage:** `docs/phase2_instrumentation_backlog.md` (Tier 0/1/2, OC-01 bis OC-05), `docs/phase2_rdc_gap_analysis.md`, Erfahrungen aus Phase 1+2

## Zweck

Erfolgsfaktoren, Barrieren und Mindest-Voraussetzungen für die Integration von CO₂-KPIs in Software-Lifecycles — destilliert aus Phase 1 (Framework-Aufbau) und Phase 2 (Prozessintegration) dieses Projekts. Gedacht als Übertragungshilfe für weitere Piloten oder Teams, nicht als DHL-spezifisches Regelwerk.

## Erfolgsfaktoren

1. **Ein SSOT statt verteilter Tabellen.** Alle KPI-Definitionen, Schwellenwerte und Mappings leben in versionierten YAML-Dateien (`data/*.yaml`), aus denen Berichte deterministisch generiert werden (`generators/build_exports.py`). Das verhindert, dass Präsentationen und Kundendokumente auseinanderlaufen — ein Risiko, das in diesem Projekt bereits einmal real aufgetreten ist (ältere Snapshot-Exporte mit 17 statt 19 KPIs kursierten parallel zum aktuellen Stand).
2. **Proxy-Kennzeichnung von Anfang an.** Jeder KPI trägt `data_coverage`, `representation_risk`, `proxy_refs` und `status: candidate`, bevor ein einziger echter Messwert vorliegt. Das macht das Framework von Tag 1 auditierbar, statt Proxy-Status erst nachträglich zu rekonstruieren.
3. **Funktionale Einheiten früh und verbindlich fixieren.** `R1` (1 CI/CD-Run) und `R2a` (1 Service-Request) wurden in Phase 1 entschieden, bevor Messwerte existierten. Ohne diese Fixierung wäre jeder spätere KPI-Vergleich zwischen Piloten methodisch angreifbar.
4. **Tier-gestaffelte Instrumentierung statt Big-Bang.** Der Instrumentation Backlog (Tier 0 → 1 → 2, ~3,25 PT → ~7 PT → ~14,5 PT) erlaubt, mit Proxy-Qualität zu starten und Qualität schrittweise zu erhöhen, statt auf eine vollständige Live-Telemetrie-Lösung zu warten, bevor überhaupt ein erster Wert existiert.
5. **Green Gates als Frühwarnsystem, nicht als Bestrafung.** Grün/Amber/Rot mit definierter `sustained_rule` (z. B. „3 aufeinanderfolgende rote Läufe") verhindert Overreaction auf Einzelausschläge und schafft Akzeptanz bei den Teams, deren Pipelines beobachtet werden.
6. **Simulationsschicht unabhängig vom Pilot-Blocker vorantreiben.** Die Pareto-/Sensitivitätsanalyse (`generators/rdc_pareto.py`) und die 192-Szenarien-Simulation liefen weiter, obwohl OC-01 bis OC-05 ungeklärt blieben — Entscheidungsfähigkeit entsteht so parallel zur Pilot-Klärung statt danach.

## Barrieren

1. **Pilot-Scope-Klärung als zentraler Flaschenhals.** Alle fünf offenen Punkte (OC-01 bis OC-05: Pipeline, Service, Region/RZ, APM-Tool, Asset-Owner) blockieren gemeinsam den Übergang von Proxy- zu Beobachtungsqualität. Ohne sie bleibt jede KPI-Berechnung methodisch korrekt, aber inhaltlich hypothetisch.
2. **Governance/RACI unbesetzt (GAP-004).** Rollen (KPI Owner, Data Steward, Boundary Curator, Data Quality Owner, Release Approver, Audit Liaison) sind definiert, aber namentlich nicht besetzt. Ohne Besetzung bleibt jede Eskalationslogik (Green Gates) folgenlos.
3. **Lizenz- und Kostenschwellen bei Live-Feeds.** Electricity Maps ist ab der Freigrenze (10.000 Anfragen/Monat) kommerziell; IEA/EMBER-Daten sind ab kommerzieller Nutzung kostenpflichtig. Das beeinflusst, welche Tier-1-Maßnahme zuerst wirtschaftlich vertretbar ist.
4. **Unsicherheit im Embodied-Carbon-Term ohne Herstellerdaten.** Ohne Vendor-PCF-Datenblatt liegt `embodied_co2_kg` nur als TDP-Proxy vor (±50 % Unsicherheit) — ausreichend für Entscheidungsrichtung, nicht für Auditierbarkeit.

## Mindest-Voraussetzungen (Minimal Viable Instrumentation)

Bevor ein Pilot überhaupt Proxy-Qualität liefern kann, muss Tier 0 vollständig sein (~3,25 PT Gesamtaufwand):

| Voraussetzung | Ohne die: |
|---|---|
| Pilot-Pipeline benannt (OC-01) | BLD-001/003 bleiben ohne jeden Ankerpunkt |
| Pilot-Service benannt (OC-02) | RUN-001/002 bleiben ohne jeden Ankerpunkt |
| Region/Rechenzentrum bestätigt (OC-03) | Carbon-Intensity-Feed kann nicht gebunden werden |
| APM-Lösung benannt (OC-04) | Request-Zähler (R2a) lässt sich nicht aktivieren |
| Asset-Owner benannt (OC-05) | Hardware-Inventar bleibt unzugänglich, HW-001 bleibt reiner Proxy |

Erst wenn alle fünf erfüllt sind, ist der Übergang von „candidate/proxy" zu „beobachtet" (Maturity M1→M2) für die betroffenen KPIs möglich.

## Übertragbare Lektionen

- SSOT + deterministische Exporte zuerst bauen, dann erst Kundendokumente daraus ableiten — nie umgekehrt.
- Proxy-Status ist ein Feature, kein Makel: sichtbare Unsicherheit schafft mehr Vertrauen als verschwiegene Präzision.
- Simulationsfähigkeit lässt sich vom Datenzugriff entkoppeln — das erhält Projektmomentum, während organisatorische Klärungen laufen.
