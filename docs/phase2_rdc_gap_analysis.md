# Gap-Analyse: RDC-Konzept vs. DHL CO₂-Artefakt Phase 2

**Datum:** 2026-05-29  
**Kontext:** Konsolidierung eines extern erarbeiteten GPU/Resource-Decision-Compiler-Modells (RDC) mit dem bestehenden DHL CO₂-Artefakt-Repo (Phase 1 abgeschlossen, Phase 2 in Vorbereitung)  
**Zweck:** Belastbare Bestandsaufnahme — was ist vorhanden, was fehlt, was lässt sich direkt integrieren, was gehört in Phase 3.

---

## 1. Ausgangslage: Was ist im Repo vorhanden

### 1.1 Datenmodell (SSOT)
| Datei | Inhalt | Status |
|---|---|---|
| `data/kpis.yaml` | 17 KPI-Kandidaten (SCI, BLD, RUN, INF, GOV) | Phase 1 vollständig |
| `data/assumptions_proxies.yaml` | 3 Assumptions, 5 Gaps, 4 Proxies | Phase 1; GAP-003/004/005 noch offen |
| `data/lifecycle_mapping.yaml` | 17 KPI-to-Lifecycle-Mappings (8 Steps) | Phase 1 vollständig |
| `schema/kpis.schema.json` | Striktes JSON-Schema (28 Pflichtfelder je KPI) | Produktiv, CI-validiert |

### 1.2 Generatoren & Exports
| Modul | Funktion |
|---|---|
| `generators/build_exports.py` | Deterministischer Export: 6 MD + 1 CSV aus YAML |
| `ci/validate_and_export.py` | CI-Einstiegspunkt; verifiziert alle Exports |

### 1.3 KPI-Systematik
Die 17 bestehenden KPIs messen entlang der SCI-Formel `((E * I) + M) / R`:

- **E** — Energieverbrauch (Wh): BLD-001…003, RUN-001…004, INF-001…003
- **I** — Kohlenstoffintensität (gCO₂e/kWh): durch GAP-001 noch proxy-basiert
- **M** — Embodied Carbon (Hardware-Amortisierung): BLD-004, BLD-005 — **GAP-003 noch offen**
- **R** — Functional Unit: R1 = 1 CI/CD-Run (fix), R2a = 1 Service-Request (fix)

### 1.4 Phase-2-Plan (Vorgehensvorschlag 2026-05-07)
Sechs geplante Deliverables:
1. Prozessintegrationsmodell (Green DevOps)
2. Design Principles & Green Gates (Schwellenwerte: grün/amber/rot)
3. KPI-to-Process-Mapping
4. Best Practices
5. Priorisiertes Instrumentation-Backlog (Tier 0/1/2)
6. Aktualisierte Gap-Analyse (Closure GAP-003, GAP-005 für Pilot-Scope)

Explizit im Phase-2-Plan beschrieben, aber noch nicht implementiert:
- Fünfstufiges Reifegradmodell je KPI (ad-hoc → audit-capable)
- RACI-Matrix (6 Rollen)
- Green Gates mit Eskalationslogik
- Embodied Carbon Methode (= GAP-003-Closure)
- Instrumentierungs-Backlog (Eco-CI, Kepler, Scaphandre, OpenTelemetry)

---

## 2. Was das RDC-Konzept einbringt

Das in einem separaten Chatverlauf entwickelte **Resource Decision Compiler (RDC)**-Modell ist eine Abstraktion einer GPU-Kaufentscheidung zu einem allgemeinen Optimierungsoperator für energie- und kostenbewusste KI-Infrastruktur.

### 2.1 Kernentitäten des RDC-Modells

```
HardwareConfig:
  vram_total_gb, vram_effective_gb
  power_idle_w, power_load_w
  capex_eur, expected_lifetime_months
  maintenance_risk, software_maturity
  embodied_co2_kg

Workload:
  model_size_b, quantization, context_length, batch_size
  expected_requests_per_month
  quality_score, business_value_score

Measurement:
  latency_ms, tokens_input/output
  energy_joule, gpu_utilization_avg
  vram_used_gb, cost_eur, co2_kg
```

### 2.2 Mathematischer Kern

**Kapazitätsbedingung:**
```
MemoryRequired(model, quant, ctx, batch) ≤ EffectiveVRAM(cluster)
EffectiveVRAM = Σ VRAM_i × η_parallel   (η ≈ 0.75–0.95)
```

**CO₂-Modell Build/Run:**
```
CO2_build_amortized = Σ EmbodiedCO2_hardware_i / LifetimeOutputs
CO2_run = Energy_kWh × EmissionFactor
EmissionFactor = f(PV_share, grid_share, battery_share, time_of_day)
```

**Kosten pro nützlichem Ergebnis:**
```
CostUsefulOutcome = (CAPEX_ann + EnergyCost + MaintenanceCost) / UsefulOutputs
UsefulOutputs = Outputs × QualityScore × BusinessValueScore
```

**EfficiencyScore (Pareto-Bewertung Hardware):**
```
Score = w1×VRAM/€ + w2×VRAM/W + w3×Throughput/W
      + w4×SoftwareMaturity + w5×Reliability + w6×UpgradePath
      - w7×MaintenanceRisk - w8×ComplexityPenalty
```

**RDC-Operator (abstrakt):**
```
RDC(x) = argmax_c Utility(c, w)
subject to:
  MemoryFeasible(c, w)
  Budget(c) ≤ B
  Risk(c) ≤ R_max
  CO2(c) ≤ C_max
```

### 2.3 Simulationskonzept (Stellvariablen)
Das RDC-Modell erlaubt parametrisierte Simulationen: beliebige Stellvariablen (z.B. Anzahl GPUs, Quantisierung, Batch-Größe, PV-Anteil, CO₂-Budget) können variiert werden, um wissenschaftlich belastbare Szenarien zu erzeugen. Dieses Konzept ist im aktuellen Repo nicht vorhanden.

---

## 3. Gap-Analyse: Differenz RDC-Konzept vs. Repo-Stand

### 3.1 Dimensionen im Vergleich

| Dimension | Repo-Stand (Phase 1) | RDC-Konzept | Gap | Priorität |
|---|---|---|---|---|
| **SCI-Formel** | `((E×I)+M)/R` vollständig definiert | Kompatibel (E, I, M, R) | Kein Gap | — |
| **Embodied Carbon (M)** | BLD-004/005 als Kandidaten; GAP-003 offen | Konkrete Formel: `EmbodiedCO2/LifetimeOutputs` | **GAP-003 schließbar** | Phase 2 |
| **Energiemodell Run** | RUN-001/002 (gCO₂e/Request, Wh/Request) | `EnergyPerToken`, `EnergyPerWorkflow` (feiner) | Granularität fehlt | Phase 2 |
| **Hardware-Entität** | Nicht vorhanden (kein HardwareConfig-Datenmodell) | Vollständige Entität mit CAPEX, VRAM, Lifetime | **Neues Modul nötig** | Phase 2 |
| **CAPEX-Amortisierung** | PRX-003: lineare Amortisierung (proxy, quality: low) | Formal definiert als `CAPEX_ann + EmbodiedCO2_ann` | PRX-003 aufwertbar | Phase 2 |
| **PV/Grid-Mix** | GAP-001: RegionaI-Proxy geplant → ElMaps | `EmissionFactor = f(PV, Grid, Battery, ToD)` | Zukünftige Erweiterung | Phase 3 |
| **EfficiencyScore (Pareto)** | Nicht vorhanden (nur Green Gates: grün/amber/rot) | Gewichteter Multi-Kriterien-Score | Phase-2 Design Principles | Phase 2 |
| **Simulation (Stellvariablen)** | Nicht vorhanden | RDC-Operator: `argmax Utility(c,w)` | **Neues Konzept** | Phase 3 |
| **UsefulOutput (Qualitätsgewichtung)** | Nicht vorhanden | `Outputs × QualityScore × BusinessValueScore` | Erweiterung RUN-KPIs | Phase 3 |
| **WorkloadProfiler** | Nicht vorhanden | Entität: model_size, quant, context, batch | Phase-3-Vorbereitung | Phase 3 |
| **Instrumentation** | Roadmap vorhanden (Eco-CI, Kepler, DCGM) | DCGM + Prometheus für VRAM/Power | Kompatibel, ergänzend | Phase 2 |
| **Governance / RACI** | Geplant für Phase 2 | Nicht Teil RDC | Kein Konflikt | Phase 2 |

### 3.2 Zusammenfassung nach Integrationszeitpunkt

**Sofort integrierbar (Phase 2):**
- GAP-003 schließen mit konkreter Amortisierungs-Formel aus dem RDC-Modell
- `data/hardware_configs.yaml`: HardwareConfig-Entität als neues Datenmodell
- `generators/hardware_model.py`: EfficiencyScore + CO₂-Build/Run-Rechner
- Zwei neue KPI-Kandidaten: HW-001 (Embodied CO₂/Request) und HW-002 (CAPEX/Request)
- PRX-003 von "quality: low" auf "quality: medium" upgraden (konkrete Methode hinterlegt)

**In Phase 3 (Simulation + Operationalisierung):**
- RDC-Operator als formale Spezifikation
- WorkloadProfiler-Entität
- Stellvariablen-Simulation (parametrisierte Szenarien)
- PV/Grid-Mix EmissionFactor-Erweiterung
- UsefulOutput-Qualitätsgewichtung
- Dashboard-Wireframe-Erweiterung um Hardware-Tier

---

## 4. Konkrete Integrationsempfehlung Phase 2

### 4.1 GAP-003 schließen (Embodied Carbon Methode)

**Methode:** Lineare Amortisierung mit inventory-gespeistem Startwert.

```
EmbodiedCO2_per_request =
  EmbodiedCO2_hardware_kg × 1000 × (gCO2e/kg)
  / (LifetimeMonths × RequestsPerMonth)

EmbodiedCO2_ann_gCO2e = EmbodiedCO2_hardware_kg × 1000 / LifetimeYears
```

Inventory-Quelle Priorität: Herstellerangabe (z.B. NVIDIA PCF) > Ecoinvent-Datenbank > generischer Proxy (0.5 kg CO₂e/W TDP als Fallback).

### 4.2 Neue KPI-Kandidaten (HW-Gruppe)

Zwei neue KPI-Kandidaten für das KPI-Catalog-Datenmodell:

| ID | Name | Formel | Schließt |
|---|---|---|---|
| HW-001 | Embodied CO₂ per Request | `EmbodiedCO2_total_gCO2e / R_total` | GAP-003 |
| HW-002 | CAPEX amortized per Request | `(CAPEX_eur / LifetimeMonths × 12) / RequestsPerMonth` | — |

### 4.3 EfficiencyScore für Hardware-Auswahlentscheidungen

Im Phase-2-Deliverable "Design Principles" kann der EfficiencyScore als dokumentiertes Bewertungsschema aufgenommen werden (nicht als operativer KPI, sondern als Entscheidungshilfe für Infra-Teams):

```yaml
efficiency_score_weights:
  vram_per_eur: 0.25
  vram_per_watt: 0.15
  throughput_per_watt: 0.15
  software_maturity: 0.15
  reliability: 0.10
  upgrade_path: 0.10
  maintenance_risk: -0.05
  complexity_penalty: -0.05
```

### 4.4 Simulation — Phase-3-Prep-Artefakt

Das RDC-Konzept liefert exakt das, was der Phase-2-Plan als "Phase-3-Vorbereitung" vorsieht:
- **KPI-Datenmodell-Sketch** → HardwareConfig + Workload + Measurement-Entitäten
- **Datenfluss-Diagramm** → Telemetrie → Transformation → KPI → Visualisierung
- **Dashboard-Wireframe-Skeleton** → Engineering, Platform Control, Management

Der RDC-Operator (`argmax Utility(c,w)`) ist die formale Grundlage für die Simulationsschicht.

---

## 5. Wissenschaftliche Belastbarkeit

### 5.1 Was ist belegt
- SCI-Formel: GSF Specification v1.1.0, ISO 14064-1:2018
- Lineare Amortisierung: GHG Protocol, Ecoinvent-Konventionen
- VRAM/Power-Metriken: NVIDIA DCGM, nvml, öffentliche Datasheets

### 5.2 Was sind Annahmen/Proxies
- η_parallel (Multi-GPU-Effizienz): empirischer Schätzwert, muss per Benchmark validiert werden
- EmbodiedCO2-Startwert ohne PCF-Datenblatt: ±50% Unsicherheit
- QualityScore / BusinessValueScore: unternehmensspezifisch, nicht standardisiert

### 5.3 Validierungsstrategie
1. Embodied-CO2-Inventar aus NVIDIA-PCF-Datenblättern beziehen (öffentlich für ausgewählte Karten)
2. η_parallel durch vLLM-Benchmark auf konkretem Cluster messen
3. CO₂-Modell gegen CodeCarbon/Eco-CI-Messungen validieren

---

## 6. Entscheidung empfohlen

| Frage | Empfehlung |
|---|---|
| GAP-003 in Phase 2 schließen? | Ja — konkrete Methode liegt vor, ist in YAML-Proxy umsetzbar |
| HardwareConfig-Modul in Repo? | Ja — als eigenständiges Datenmodell (nicht in kpis.yaml) |
| EfficiencyScore im Phase-2-Deliverable? | Ja — als Design-Principle-Dokument, nicht als operativer KPI |
| Simulation (RDC-Operator) in Phase 2? | Nein — als Phase-3-Prep-Dokument, nicht als Implementierung |
| Neue HW-KPIs in kpis.yaml? | Optional Phase 2 — nur HW-001 (Embodied) ist Phase-2-relevant |
