# Phase 3 Prep: RDC-Operator & Stellvariablen-Simulation

**Datum:** 2026-05-29  
**Status:** Phase-3-Vorbereitungsartefakt (nicht Phase-2-Scope)  
**Basis:** Resource Decision Compiler (RDC) aus Adaptive-Agent-OS-Kontext, angepasst auf DHL CO₂-Artefakt

---

## 1. Ziel

Die Simulationsschicht macht das KPI-Framework **entscheidungsfähig**: Statt statischer Schwellenwerte können beliebige Stellvariablen variiert werden, um Szenarien wissenschaftlich belastbar durchzurechnen. Das erlaubt DHL-Teams:

- "Was-wäre-wenn"-Analysen: Wie verändert sich CO₂/Request bei 2× mehr Traffic?
- Hardware-Auswahl auf Basis konkreter Ziel-KPIs
- Optimierung zwischen konkurrierenden Zielen (Kosten, CO₂, Latenz, Verfügbarkeit)

---

## 2. RDC-Operator (formal)

```
RDC(x) = argmax_c  Utility(c, w)
subject to:
  CapacityFeasible(c, w)     # VRAM >= Workload-Bedarf
  CAPEX(c)     ≤ B           # Budget-Constraint
  Risk(c)      ≤ R_max       # Maintenance-Risk
  CO2(c, w)    ≤ C_max       # CO2-Budget je Request
```

Dabei:
- `c` — HardwareConfig (aus `data/hardware_configs.yaml`)
- `w` — WorkloadProfile (Modellgröße, Quantisierung, Traffic)
- `Utility(c, w)` = EfficiencyScore(c) × QualityScore(w) × BusinessValueScore(w)

Der RDC ist bereits als `generators/hardware_model.py::rdc_rank()` implementiert (Phase-2-Stub).

---

## 3. Datenflussbild (Phase 3)

```
Stellvariablen (Input)
  │
  ▼
┌──────────────────────────────────────────────────┐
│ WorkloadProfiler                                 │
│   model_size_b, quantization, context_length,    │
│   batch_size, requests_per_month                 │
│   → min_vram_gb, expected_energy_per_request     │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ CapacityCheck                                    │
│   EffectiveVRAM(cluster) >= MemoryRequired       │
│   η_parallel correction applied                  │
└──────────────────┬───────────────────────────────┘
                   │  (feasible configs only)
                   ▼
┌──────────────────────────────────────────────────┐
│ CostModel         │ EnergyModel  │ CO2Model       │
│ HW-002 CAPEX/req  │ Energy/kWh   │ HW-001 embed.  │
│ OpEx/req          │ EF=f(PV,Grid)│ RUN CO2/req    │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ ParetoOptimizer                                  │
│   Dimensions: CO2/req, EUR/req, Latenz, VRAM     │
│   Output: Pareto-Frontier + EfficiencyScore-Rank  │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│ DeploymentRecommendation                         │
│   Top-N Configs + Begründung                     │
│   Sensitivitätsanalyse: Δco2 / ΔStellevariable   │
└──────────────────────────────────────────────────┘
```

---

## 4. Stellvariablen (Simulation-Parameter)

### 4.1 Workload-Stellvariablen
| Variable | Typ | Wertebereich | Effekt |
|---|---|---|---|
| `model_size_b` | float | 7–405 | VRAM-Bedarf, Latenz |
| `quantization` | enum | INT4/INT8/FP16 | VRAM × 0.25–1.0 |
| `requests_per_month` | int | 1k–10M | Amortisierungseffekt |
| `context_length` | int | 512–128k | KV-Cache VRAM |
| `batch_size` | int | 1–256 | Throughput vs. Latenz |

### 4.2 Hardware-Stellvariablen
| Variable | Typ | Wertebereich | Effekt |
|---|---|---|---|
| `gpu_count` | int | 1–8 | EffectiveVRAM, η_parallel |
| `capex_eur` | float | 1k–50k | HW-002, CostUsefulOutcome |
| `expected_lifetime_months` | int | 12–96 | Amortisierungsrate |
| `power_load_w` | float | 150–1400 | RunCO2, Energiekosten |

### 4.3 Energie- und CO₂-Stellvariablen
| Variable | Typ | Wertebereich | Effekt |
|---|---|---|---|
| `pv_share` | float | 0.0–1.0 | EmissionFactor sinkt |
| `grid_ef_gco2e_per_kwh` | float | 41–800 | RunCO2 direkt |
| `energy_cost_eur_per_kwh` | float | 0.05–0.50 | OpEx |
| `battery_share` | float | 0.0–0.5 | EmissionFactor |

### 4.4 Geschäftliche Stellvariablen
| Variable | Typ | Wertebereich | Effekt |
|---|---|---|---|
| `quality_score` | float | 0.0–1.0 | UsefulOutputs, CostUsefulOutcome |
| `business_value_score` | float | 0.0–1.0 | UsefulOutputs |
| `co2_budget_gco2e_per_request` | float | 0.001–10.0 | RDC-Filter |
| `capex_budget_eur` | float | 1k–inf | RDC-Filter |

---

## 5. Wissenschaftliche Belastbarkeit

### 5.1 Validierte Größen
| Größe | Quelle |
|---|---|
| SCI-Formel | GSF Specification v1.1.0 |
| Embodied CO₂ (Formel) | GHG Protocol, Ecoinvent-Konventionen |
| Deutsche Grid-Emissionsfaktor | UBA 2024: 485 gCO₂e/kWh |
| PV-Lifecycle-Emissionen | Fraunhofer ISE: ~41 gCO₂e/kWh |
| Multi-GPU η_parallel | Empirisch zu validieren (vLLM-Benchmark) |

### 5.2 Unsicherheiten
| Größe | Unsicherheit | Validierungsstrategie |
|---|---|---|
| embodied_co2_kg (proxy) | ±50% | NVIDIA PCF-Datenbläter abrufen |
| η_parallel | ±10–20% | vLLM-Benchmark auf echtem Cluster |
| EmbodiedCO2-Proxy (0.5 kg/W) | ±50% | Ecoinvent-Datenbank für bekannte GPU-Modelle |
| quality_score | subjektiv | Unternehmensseitig zu kalibrieren |

---

## 6. Erweiterungspfad

```
Phase 2 (aktuell):
  hardware_model.py → RDC-Stub (filter + rank, deterministisch)
  hardware_configs.yaml → 5 Referenz-Konfigurationen

Phase 3 (operativ):
  SimulationEngine → parametrisierte Szenario-Läufe
  ParetoFrontier → mehrdimensionale Optimierung
  WorkloadProfiler → Auto-Kalibrierung aus Telemetrie

Phase 4 (Echtzeit):
  EmissionFactor-Feed → Electricity Maps API (stündlich, regional)
  DCGM-Telemetrie → Live-VRAM/Power-Metriken
  CO2-Budget-Gate → automatische Release-Entscheidung
```

---

## 7. Abgrenzung zur Phase-2-Green-Gate-Logik

Phase 2 definiert **statische Schwellenwerte** (grün/amber/rot) je KPI.  
Phase 3 ergänzt das durch **dynamische Optimierung**: Schwellenwerte werden nicht fix gesetzt, sondern aus dem RDC-Operator abgeleitet — abhängig von Workload, Hardware, Energiemix und Businesskontext.

Komplementarität, kein Konflikt: Green Gates bleiben als operative Eskalationslogik bestehen. Der RDC-Operator informiert, wo die Schwellenwerte sinnvoll gesetzt werden sollten.

---

## 8. Datenmodell-Sketch (Phase-3-Deliverable)

Kernentitäten und Relationen:

```
SystemBoundary ──1:n── HardwareConfig
HardwareConfig ──1:n── Measurement
WorkloadProfile ──1:n── Measurement
Measurement ──n:1── EmissionFactorProfile
Measurement ──n:1── KPI_Result
KPI_Result ──n:1── KPI (aus kpis.yaml)
KPI_Result ──n:1── GreenGateDecision
GreenGateDecision ──1:1── ReleaseDecision
```

Jede `Measurement`-Instanz entsteht aus:
- Telemetrie (DCGM, Kepler, OpenTelemetry)
- ODER Simulation (RDC-parametrisiert)

Das erlaubt eine einheitliche KPI-Berechnung für beide Quellen.
