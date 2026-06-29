# Phase 2 KPI-to-Process-Mapping

## Grundlage

Quelle ist `data/lifecycle_mapping.yaml`. Die 19 bestehenden KPI-Kandidaten bleiben maßgeblich.

| KPI | Prozessanker | Green-Gate-Ort | Owner-Rolle | Entscheidungspunkt |
|---|---|---|---|---|
| SCI-001 | Monitor | Portfolio-/Service-Review | KPI Owner | SCI-Rate gegen Zielkorridor prüfen |
| SCI-002 | Monitor | Reporting-Freigabe | Audit Liaison | kompatible Perioden- und Boundary-Versionen aggregieren |
| BLD-001 | Build | Release | Release Approver | Pipeline-Lauf akzeptieren, beobachten oder eskalieren |
| BLD-002 | Test | Testabschluss | Data Quality Owner | Testumgebung verkleinern, abschalten oder weiterlaufen lassen |
| BLD-003 | Build/Release | Release | Release Approver | Build-Dauer und Artefaktfrequenz prüfen |
| BLD-004 | Build/Test | Modell- oder Trainingsfreigabe | KPI Owner | Trainingslauf begründen oder verschieben |
| BLD-005 | Plan/Build | Planungsreview | Boundary Curator | Hardwareanteil auf Planungseinheit allokieren |
| RUN-001 | Operate/Monitor | Service-Review | KPI Owner | Emissionen pro Request/Transaktion bewerten |
| RUN-002 | Operate | Service-Review | Data Steward | Energie pro Request gegen Zielwert prüfen |
| RUN-003 | Deploy/Operate | Architekturreview | KPI Owner | Datenübertragung, Routing oder Caching anpassen |
| RUN-004 | Monitor/Operate | Kapazitätsreview | Data Quality Owner | Auslastung und Energieproportionalität bewerten |
| INF-001 | Operate/Monitor | Plattformreview | Boundary Curator | PUE als Kontextfaktor anwenden |
| INF-002 | Operate/Monitor | Plattformreview | KPI Owner | CUE und regionale Platzierung bewerten |
| INF-003 | Monitor/Operate | Kapazitätsreview | Data Steward | Auslastung, Autoscaling und Idle-Kapazität prüfen |
| GOV-001 | Monitor/Plan | Reporting-Freigabe | Data Quality Owner | Vollständigkeit für Veröffentlichung prüfen |
| GOV-002 | Monitor/Plan | jede KPI-Freigabe | Data Quality Owner | Maturity-Level vergeben |
| GOV-003 | Monitor/Plan/Operate | Audit-Review | Audit Liaison | Allokationsregel und Doppelzählung prüfen |
| HW-001 | Deploy/Plan | Infrastrukturreview | Boundary Curator | Embodied Carbon pro Request bewerten |
| HW-002 | Plan/Operate | Beschaffungsreview | KPI Owner | CAPEX/OPEX pro Request vergleichen |

## Offene DHL-Eingaben

- konkrete CI/CD-Pipeline
- konkreter Run-Service
- Region oder Rechenzentrum
- APM-/Observability-System
- Hardware-Inventar und Asset Owner
- namentliche Rollenbesetzung
