# Phase 2 Tier-0 Pilot Setup

## Zweck

Tier 0 beschreibt die Mindestvoraussetzungen für eine messbare Build- und Run-Demonstration. Die Angaben sind Default-Profile, bis DHL konkrete Systeme und Datenverantwortliche bestätigt.

## Pilot A: CI/CD Build

| Feld | Default | DHL-Ersatzwert |
|---|---|---|
| Plattform | GitHub Actions, GitLab CI oder Azure DevOps | konkrete CI-Plattform |
| Messwerkzeug | Eco-CI | freigegebenes CI-Energie-Tool |
| Primäre KPIs | BLD-001, BLD-003 | bestätigte Build-KPIs |
| Benötigte Daten | Pipeline-ID, Runner-Typ, Laufzeit, Runner-/Cloud-Billing | konkrete Metriken |

Minimaler Ablauf:

1. Repräsentative Pipeline auswählen.
2. Eco-CI oder äquivalentes Plugin in einem nicht-produktiven Pilotlauf aktivieren.
3. Pipeline-Laufzeit, geschätzte Energie und Carbon-Intensity-Quelle erfassen.
4. BLD-001 und BLD-003 als Proxy- oder beobachtbare Werte kennzeichnen.

## Pilot B: Run Service

| Feld | Default | DHL-Ersatzwert |
|---|---|---|
| Plattform | Kubernetes/OpenTelemetry-Service | konkreter Run-Service |
| Messwerkzeug | Kepler für Kubernetes, Scaphandre für Bare Metal | freigegebenes Observability-Tool |
| APM | OpenTelemetry-neutral | Datadog, Dynatrace oder vorhandenes APM |
| Primäre KPIs | RUN-001, RUN-002, RUN-004, HW-001 | bestätigte Run-KPIs |

Minimaler Ablauf:

1. Servicegrenze und Request-Zähler definieren.
2. Kepler oder Scaphandre in der Pilotumgebung anbinden.
3. Energie, Request-Volumen, Laufzeit und Carbon-Intensity-Quelle erfassen.
4. RUN-001, RUN-002 und HW-001 mit Maturity-Level kennzeichnen.

## Gemeinsame Tier-0-Eingaben

| Eingabe | Default | Status |
|---|---|---|
| Region/RZ | Deutschland nationaler Durchschnitt | ersetzbar |
| Carbon-Intensity-Quelle | UBA-DE-STROMMIX-2024 | Proxy/Benchmark |
| Hardware-Inventar | Template in `data/hardware_inventory_template.yaml` | DHL-Export offen |
| PUE | 1,5 als Platzhalter | RZ-Wert offen |
| Rollen | Platzhalter gemäß `phase2_pilot_defaults.yaml` | DHL-Besetzung offen |

## Ergebnis

Tier 0 liefert keine auditfähige DHL-Baseline. Lieferbar sind ein reproduzierbarer Pilotablauf, erste beobachtbare oder proxybasierte KPI-Werte und eine belastbare Liste der fehlenden produktiven Datenbindungen.
