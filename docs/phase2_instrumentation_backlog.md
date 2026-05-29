# Phase 2 Instrumentation Backlog

**Datum:** 2026-05-29  
**Status:** Phase-2-Deliverable (Entwurf)  
**Bezug:** Vorgehensvorschlag 2026-05-07 §4.4 — Instrumentation Backlog & Embodied Carbon Method

---

## Überblick

Drei Tier-Stufen strukturieren die Instrumentierungsreihenfolge nach Pilotrelevanz und Aufwand.

| Tier | Bezeichnung | Zweck |
|---|---|---|
| **Tier 0** | Pilot-Voraussetzungen | Minimales Set, das den Pilot A (Build) und Pilot B (Run) lauffähig macht |
| **Tier 1** | Pilot-Skalierung | Erweitert Tier 0 auf weitere Pipelines / Services im Pilotbereich |
| **Tier 2** | Organisationsweite Generalisierung | Vollständige Integration in DHL-Landschaft; abhängig von Phase-3-Entscheidungen |

---

## Tier 0 — Pilot-Voraussetzungen

*Ziel: Pilot A + B können CO₂-KPIs liefern (auch mit Proxies). Alles andere ist geblockt.*

| # | Maßnahme | Betroffene KPIs | Tool / System | Aufwand | Lizenz | Blocker |
|---|---|---|---|---|---|---|
| T0-01 | CI-Pipeline-Energie messen | BLD-001, BLD-003 | [Eco-CI](https://github.com/green-coding-solutions/eco-ci-energy-estimation) (GitHub Actions / GitLab CI Plugin) | 0.5 PT | MIT | Pilot-Pipeline muss identifiziert sein (§6.2 offen) |
| T0-02 | Laufzeit-Energie messen (Run-Service) | RUN-001, RUN-002 | [Kepler](https://github.com/sustainable-computing-io/kepler) (Kubernetes) oder [Scaphandre](https://github.com/hubblo-org/scaphandre) (Bare Metal) | 1 PT | Apache 2.0 | Zugriff auf Cluster-Node (DHL-Infra-Team) |
| T0-03 | Carbon Intensity Feed einbinden | Alle SCI-KPIs | UBA-Tabellenwert (statisch, Phase 1) → IEA/EMBER (Phase 2 API) | 0.5 PT | IEA: kostenpflichtig ab komm. Nutzung | Standort / Rechenzentrum bestätigen |
| T0-04 | Request-Zähler aktivieren (R2) | RUN-001 bis RUN-004 | APM-System des Pilots (Datadog / Dynatrace / OpenTelemetry) | 0.5 PT | nach vorhandenem Lizenzmodell | Zugriff auf APM-Config (DHL-Monitoring-Team) |
| T0-05 | Hardware-Inventar für Pilot erfassen | HW-001, BLD-004, BLD-005 | Asset-Management-Export (CSV) | 0.5 PT | intern | DHL Asset-Owner benennen (RACI Boundary Curator) |
| T0-06 | PUE des Pilot-Rechenzentrums erfragen | INF-001, INF-002 | Datacenter-Betrieb (Messwert oder Standardwert 1.5) | 0.25 PT | intern | Ansprechpartner RZ-Operations |

**Tier-0-Gesamtaufwand:** ~3,25 PT  
**Output:** Pilot A und B liefern BLD-001, RUN-001, RUN-002, HW-001 mit Proxy-Qualität.

---

## Tier 1 — Pilot-Skalierung

*Ziel: Proxy-Qualität verbessern, weiterer Build-/Run-Scope, erste Dashboard-Integration.*

| # | Maßnahme | Betroffene KPIs | Tool / System | Aufwand | Lizenz | Abhängigkeit |
|---|---|---|---|---|---|---|
| T1-01 | Granulare Pipeline-Metriken (Stage-Level) | BLD-001, BLD-002, BLD-003 | Eco-CI + CI-Stage-Tags | 1 PT | MIT | T0-01 abgeschlossen |
| T1-02 | Embodied-CO₂-Inventar: Vendor-PCF-Datenbläter | HW-001 (Qualität: low→medium) | Vendor-Sustainability-Reports (PDF-Import) | 1 PT | offen je Hersteller | T0-05; PCF-Verfügbarkeit klären |
| T1-03 | Real-Time Carbon Intensity (stündlich, regional) | SCI-001, SCI-002, RUN-001 | [Electricity Maps API](https://www.electricitymaps.com/) | 1.5 PT | kommerziell (Freigrenze 10k req/mo) | API-Key + Standort-Mapping |
| T1-04 | OpenTelemetry-Exporter für CO₂-Metriken | Alle Run-KPIs | OTel Collector + Custom Exporter | 2 PT | Apache 2.0 | OTel-Infrastruktur vorhanden (T0-04) |
| T1-05 | KPI-Berechnung automatisieren (Scheduler) | Alle KPIs | Python-Job (bestehender CI-Generator erweitert) + Cron | 1 PT | intern | Datenquellen aus Tier 0 angebunden |
| T1-06 | Maturity-Assessment-Lauf (GOV-002) | GOV-001, GOV-002 | Manuelles Review + YAML-Update | 0.5 PT | intern | Tier 0 abgeschlossen |

**Tier-1-Gesamtaufwand:** ~7 PT  
**Output:** KPI-Qualität steigt von Proxy auf beobachtbar/messbar; erstes Dashboard befüllbar.

---

## Tier 2 — Organisationsweite Generalisierung

*Ziel: Von Pilot auf gesamte DHL-Softwarelandschaft skalieren. Phase-3-Voraussetzung.*

| # | Maßnahme | Betroffene KPIs | Tool / System | Aufwand | Abhängigkeit |
|---|---|---|---|---|---|
| T2-01 | CI-Energie für alle Pipelines (flächendeckend) | BLD-001 bis BLD-003 | Eco-CI als Org-weites Plugin | 3 PT | T1-01; CI-Platform-Owner-Buy-in |
| T2-02 | DCGM-Exporter für GPU-Cluster | HW-001, RUN-002, INF-003 | [NVIDIA DCGM](https://github.com/NVIDIA/dcgm-exporter) + Prometheus | 2 PT | Apache 2.0; T1-04 |
| T2-03 | Allocation-Policy-Registry aufbauen | GOV-003 | YAML-Registry (dieses Repo) | 2 PT | RACI Boundary Curator besetzt |
| T2-04 | ISO-14064-Mapping vervollständigen | GOV-001, GAP-005 | Manuelles Review + YAML-Update | 1.5 PT | ISO-Normtextzugang |
| T2-05 | ML-Training-Emissions instrumentieren | BLD-004 | [CodeCarbon](https://github.com/mlco2/codecarbon) + Training-Pipeline-Integration | 2 PT | MIT; T1-04 |
| T2-06 | Dashboard (3 Views: Engineering / Platform / Management) | Alle | Grafana + Prometheus | 4 PT | Apache 2.0; T1-04/T1-05 |

**Tier-2-Gesamtaufwand:** ~14,5 PT  
**Output:** Vollständige, audit-fähige CO₂-KPI-Plattform für DHL.

---

## Lizenz-Memo Tier 0 (kritisch)

| Tool | Lizenz | Nutzungsbeschränkung |
|---|---|---|
| Eco-CI | MIT | Keine Einschränkungen |
| Kepler | Apache 2.0 | Keine Einschränkungen |
| Scaphandre | Apache 2.0 | Keine Einschränkungen |
| OpenTelemetry Collector | Apache 2.0 | Keine Einschränkungen |
| IEA EMBER Carbon Intensity | CC BY 4.0 (Daten) | Quellenangabe erforderlich; kommerziell erlaubt |
| Electricity Maps API | Kommerziell | Freigrenze: 10.000 Anfragen/Monat; danach kostenpflichtig |
| UBA (Umweltbundesamt) Emissionsfaktoren | Open Government Data | Quellenangabe erforderlich |
| DCGM Exporter | Apache 2.0 | Keine Einschränkungen |
| CodeCarbon | MIT | Keine Einschränkungen |

---

## Offene Klärungspunkte

| # | Frage | Betrifft | Standard-Annahme bis Klärung |
|---|---|---|---|
| OC-01 | Welche konkrete Pipeline ist Pilot A? | T0-01 | Platzhalter: generische GitHub-Actions-Pipeline |
| OC-02 | Welcher Service ist Pilot B? | T0-02/T0-04 | Platzhalter: generischer Kubernetes-Service |
| OC-03 | Welches RZ / Cloud-Region für Pilot? | T0-03/T0-06 | Deutschland (DE), EF=485 gCO₂e/kWh (UBA 2024) |
| OC-04 | Vorhandene APM-Lösung (Datadog/Dynatrace/andere)? | T0-04 | OpenTelemetry als provider-neutral angenommen |
| OC-05 | Asset-Owner für Hardware-Inventar? | T0-05 | RACI Boundary Curator (noch nicht besetzt) |
