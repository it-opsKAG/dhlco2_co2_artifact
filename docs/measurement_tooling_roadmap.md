# Measurement Tooling Roadmap

> Status: Draft — Phase 2 planning artifact
> Created: 2026-03-26
> Applies to: DHLCO2 KPI Framework — operative Messbarkeit

## Zielsetzung

Dieses Dokument beschreibt den geplanten Tooling-Stack zur operativen Messung
der SCI-Komponenten (E, I, M, R). Ziel ist ein **anbieterunabhängiges,
modulares Framework**, das schrittweise um konkrete Datenquellen erweitert
werden kann — unabhängig davon, welche Systeme beim Auftraggeber im Einsatz sind.

## SCI-Formel → Tooling-Zuordnung

```
SCI = ((E × I) + M) / R
```

| SCI-Komponente | Beschreibung | Tooling-Kategorie | Phase |
|---|---|---|---|
| **E** (Energie) | Energieverbrauch in kWh | Energiemessung / APM | Phase 2–3 |
| **I** (Carbon Intensity) | gCO₂e/kWh je Region | Emissionsfaktor-Datenquelle | Phase 1 ✓ (Stufenmodell) |
| **M** (Embodied) | Herstellungsemissionen Hardware | Hardware-Inventar / LCA-Datenbank | Phase 2 |
| **R** (Funktionseinheit) | Bezugsgröße (Request, Transaktion) | Observability / Request-Zählung | Phase 1 ✓ (R2a festgelegt) |

---

## Open-Source-Tooling-Kandidaten

### Integrierte SCI-Messung

#### Green Metrics Tool (GMT)
- **Repository:** https://github.com/green-coding-solutions/green-metrics-tool
- **Lizenz:** AGPL-3.0
- **Maintainer:** Green Coding Solutions (green-coding.io)
- **Releasestand:** v2.6 (Februar 2026), aktiv gepflegt
- **Beschreibung:** Open-Source-Plattform zur Quantifizierung von Energieverbrauch und
  CO₂-Emissionen von Software über den gesamten Lebenszyklus (Software Life Cycle Analysis).
- **SCI-Alignment:** Implementiert die SCI-Formel nativ (E, I, M, R).
- **Kernfunktionen:**
  - Reproduzierbare Messungen via `usage_scenario.yml` (Configuration-as-Code)
  - **Eco CI**: CI/CD-Pipeline-Integration (GitHub Actions, GitLab, Jenkins, TeamCity)
  - Mehrere Sensor-Provider (RAPL, IPMI, PSU, Docker, CPU)
  - REST-API, Web-Dashboard, Git-Integration für Versionsvergleiche
  - CarbonDB für zentrale Datenaggregation
  - PowerHOG für prozessgranulare Energiemessung
- **Relevanz für DHLCO2:**
  - Direkt einsetzbar für BLD-001 (CI/CD-Emissionen pro Pipeline-Lauf)
  - Eco CI kann Build-Energie pro Commit/Pipeline messen
  - Perspektivisch für Run-Phase (Runtime-Messung via Container-Orchestrierung)
- **Einschränkungen:**
  - AGPL-3.0 — Lizenzkompatibilität prüfen bei DHL-Deployment
  - Aktuell primär Runtime-Phase; Lifecycle-Erweiterung auf Roadmap
  - Docker-Abhängigkeit — ggf. Anpassung für nicht-containerisierte Workloads
- **Empfehlung:** Priorität 1 für Phase 2 Evaluation

---

### Energiemessung (Komponente E)

#### Kepler (Kubernetes-based Efficient Power Level Exporter)
- **Repository:** https://github.com/sustainable-computing-io/kepler
- **Lizenz:** Apache 2.0 (CNCF Sandbox)
- **Beschreibung:** Messung des Energieverbrauchs auf Container-/Pod-/Namespace-Ebene
  in Kubernetes-Clustern via RAPL, ACPI, GPU-Metriken und trainierte ML-Modelle.
- **SCI-Relevanz:** Direkte E-Messung für Kubernetes-Workloads.
- **Stack:** Kepler → Prometheus → Grafana.
- **Relevanz für DHLCO2:** Ideal wenn DHL Kubernetes-basierte Infrastruktur betreibt.

#### Scaphandre
- **Repository:** https://github.com/hubblo-org/scaphandre
- **Lizenz:** Apache 2.0 (Rust)
- **Beschreibung:** Echtzeit-Energiemessung auf Host-, Prozess-, Container- und VM-Ebene.
  Windows 10/11 und Linux Support.
- **SCI-Relevanz:** Direkte E-Messung mit Prozessgranularität.
- **Relevanz für DHLCO2:** Windows-Support macht es relevant für on-premises Szenarien.

#### CodeCarbon
- **Repository:** https://github.com/mlco2/codecarbon
- **Lizenz:** MIT (Python)
- **Beschreibung:** Python-Bibliothek zur Schätzung von CO₂-Emissionen aus Compute
  (CPU, GPU, RAM). Kombiniert automatisch E und I.
- **SCI-Relevanz:** E + I → direkter CO₂eq-Output pro Computation.
- **Relevanz für DHLCO2:** Ideal für BLD-004 (ML-Training-Emissionen).

#### Cloud Carbon Footprint
- **Repository:** https://github.com/cloud-carbon-footprint/cloud-carbon-footprint
- **Lizenz:** Apache 2.0 (Thoughtworks)
- **Beschreibung:** Multi-Cloud-Tool (AWS, GCP, Azure) für Energie- und Emissionsberechnung
  inkl. Embodied Carbon.
- **SCI-Relevanz:** Misst E, I und M; tägliche/monatliche/jährliche Schätzungen.
- **Relevanz für DHLCO2:** Besonders wertvoll wenn DHL Cloud-Infrastruktur nutzt.

#### PowerAPI
- **Repository:** https://github.com/powerapi-ng
- **Lizenz:** Open Source (Python)
- **Beschreibung:** Software-definierte Power-Meter; prozess- und containergranulare
  Energieschätzung via Hardware Performance Counters.
- **SCI-Relevanz:** E-Messung, forschungsnahes Tool.

---

### Observability / Request-Zählung (Komponente R)

#### OpenTelemetry
- **Website:** https://opentelemetry.io
- **Lizenz:** Apache 2.0 (CNCF)
- **Beschreibung:** Industriestandard für Traces, Metriken und Logs.
  Sprachunabhängig, breites Ökosystem.
- **SCI-Relevanz:** R-Komponente (Request-Zählung via Span-Counting);
  Basis für Integrationen mit Energiemess-Tools.
- **Empfehlung:** Als Instrumentierungsstandard für das Framework vorsehen.

#### Grafana + Prometheus + Loki
- **Lizenz:** AGPL-3.0 / Apache 2.0 (CNCF)
- **Beschreibung:** Metriken, Logs und Visualisierung.
- **SCI-Relevanz:** Zentrales Dashboard für alle SCI-Komponenten.

---

## Empfohlener Stack (Zielbild)

```
┌─────────────────────────────────────────────────────┐
│                    Grafana Dashboard                 │
│          (SCI-Visualisierung je KPI + Trend)         │
├─────────────────────────────────────────────────────┤
│                     Prometheus                       │
│              (Metriken-Aggregation)                  │
├──────────┬──────────┬──────────┬────────────────────┤
│  Kepler  │Scaphandre│  GMT     │ Cloud Carbon       │
│  (K8s E) │(Host E)  │(SCI+CI) │ Footprint (Cloud)  │
├──────────┴──────────┴──────────┴────────────────────┤
│              OpenTelemetry (Instrumentation)          │
│           (Traces, Metriken, Request-Counting)       │
├─────────────────────────────────────────────────────┤
│          Carbon Intensity API (I)                    │
│   Stufe 1: UBA  │  Stufe 2: EMBER  │  Stufe 3: EM  │
└─────────────────────────────────────────────────────┘
```

## Integrationsplan

| Phase | Aktivität | Tools |
|---|---|---|
| Phase 2 | GMT Eco CI evaluieren (Pilot: 1 Pipeline) | Green Metrics Tool |
| Phase 2 | OpenTelemetry-Instrumentierung planen | OpenTelemetry |
| Phase 2 | Carbon Intensity Stufe 2 (EMBER) integrieren | EMBER API |
| Phase 3 | Prototyp: Kepler oder Scaphandre für E-Messung | Kepler / Scaphandre |
| Phase 3 | Dashboard-Wireframe mit Prometheus + Grafana | Grafana Stack |
| Umsetzung | Cloud Carbon Footprint (wenn Cloud-Infra bekannt) | CCF |
| Umsetzung | Electricity Maps API (Echtzeit-I) | Electricity Maps |
| Umsetzung | R2-Erweiterung (Sendungsbezug) bei Datenverfügbarkeit | Custom Integration |

## Lizenzübersicht

| Tool | Lizenz | Kommerziell nutzbar | Hinweis |
|---|---|---|---|
| Green Metrics Tool | AGPL-3.0 | Ja, mit Auflagen | Source-Disclosure bei Netzwerk-Deployment |
| Kepler | Apache 2.0 | Ja | CNCF Sandbox |
| Scaphandre | Apache 2.0 | Ja | – |
| CodeCarbon | MIT | Ja | – |
| Cloud Carbon Footprint | Apache 2.0 | Ja | Thoughtworks-sponsored |
| OpenTelemetry | Apache 2.0 | Ja | CNCF Standard |
| Grafana | AGPL-3.0 | Ja, mit Auflagen | Cloud-Version kommerziell |

## Nächste Schritte

1. **GMT Eco CI Pilot**: Green Metrics Tool in einer Test-Pipeline evaluieren
2. **Lizenzprüfung**: AGPL-3.0 Kompatibilität mit DHL-Anforderungen klären
3. **OpenTelemetry-Strategie**: Instrumentierungsansatz für das Framework definieren
4. **Stakeholder-Abstimmung**: Mit DHL klären, welche Infrastruktur (Cloud/K8s/On-Prem) vorliegt
