# Phase 2 Prozessintegrationsmodell

## Zweck

Das Modell ordnet die 19 bestehenden KPI-Kandidaten in den Software-Lifecycle ein und beschreibt, an welchen Prozesspunkten Messung, Bewertung und Steuerung stattfinden. Es ergänzt keine neue KPI-Logik.

## Prozessschritte

| Schritt | Ziel | Relevante Steuerung |
|---|---|---|
| Plan | Systemgrenzen, funktionale Einheiten und Verantwortlichkeiten festlegen | GOV-001, GOV-002, GOV-003, HW-002 |
| Code | Änderungen mit späterer Messbarkeit vorbereiten | Daten- und Boundary-Anforderungen |
| Build | CI/CD-Läufe erfassen und optimieren | BLD-001, BLD-003 |
| Test | Testumgebungen und Trainingsläufe erfassen | BLD-002, BLD-004 |
| Release | Green-Gate-Entscheidung vor Auslieferung | BLD-001, BLD-003, GOV-002 |
| Deploy | Infrastruktur- und Hardwarebezug dokumentieren | RUN-003, HW-001 |
| Operate | Request-, Energie- und Emissionswerte erfassen | RUN-001, RUN-002, RUN-004, INF-001, INF-002 |
| Monitor | KPI-Werte, Datenqualität und Eskalationen überwachen | SCI-001, SCI-002, INF-003, GOV-001 bis GOV-003 |
| Improve | Maßnahmen ableiten und Schwellenwerte prüfen | alle KPI-Gruppen |

## Integrationsprinzipien

1. Systemgrenze vor Präzision: Kein KPI-Wert ohne dokumentierte Boundary.
2. Messwert vor Proxy: Proxies bleiben sichtbar und werden nicht mit produktiven Messwerten vermischt.
3. Gleiche funktionale Einheit für Vergleichbarkeit: Build nutzt R1, Run nutzt R2a bis DHL eine geschäftsnähere Einheit bestätigt.
4. Green Gates nutzen Maturity-Level: Ein proxybasierter Wert darf Hinweise geben, aber keine auditfähige Aussage ersetzen.
5. Jede Berechnung erhält Owner, Quelle, Zeitpunkt, Boundary-Version und Proxy-Status.

## Rollen

| Rolle | Aufgabe |
|---|---|
| KPI Owner | KPI fachlich freigeben |
| Data Steward | Datenquelle, Felddefinition und Datenqualität pflegen |
| Boundary Curator | Systemgrenzen und funktionale Einheiten versionieren |
| Data Quality Owner | Maturity-Level und Proxy-Status prüfen |
| Release Approver | Green-Gate-Entscheidungen im Releaseprozess anwenden |
| Audit Liaison | Nachvollziehbarkeit und Nachweise sichern |
