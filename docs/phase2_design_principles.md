# Phase 2 Design Principles — Green / Sustainable DevOps

**Datum:** 2026-07-14
**Status:** Phase-2-Deliverable (D2-02, ergänzt `data/green_gates.yaml`)
**Grundlage:** `data/green_gates.yaml`, `data/hardware_configs.yaml` (EfficiencyScore-Gewichte), `docs/phase3_simulation_concept.md`, `docs/phase2_rdc_gap_analysis.md` §4.3

## Zweck

Schriftliche Design-Prinzipien für Green/Sustainable DevOps, die dem EfficiencyScore-Modell und den Green Gates zugrunde liegen. Standalone-Dokument für DHL-Stakeholder — richtet sich an Teams, die Systeme entwerfen oder Hardware/Infrastruktur auswählen, nicht nur an die Messgovernance selbst (dafür siehe `docs/phase2_process_integration_model.md`).

## Prinzip 1 — Messbarkeit vor Reduktion

Kein Reduktionsversprechen ohne KPI-Baseline. Ein Team, das CO₂ senken will, muss zuerst wissen, wo es aktuell steht (Green-Gate-Farbe, Maturity-Level). Ohne Baseline ist jede „Verbesserung" unbeweisbar und öffnet die Tür zu Greenwashing.

## Prinzip 2 — Green Gates als Frühwarnsystem

Grün/Amber/Rot ist ein Eskalations-, kein Bestrafungsmechanismus. Jedes Gate trägt eine `sustained_rule` (z. B. „7-Tage-Rolling-Average > Schwellenwert"), damit einzelne Ausschläge nicht zu Fehlalarmen führen. Schwellenwerte sind `krallmann_default` bis DHL eigene Werte vorgibt — Ersetzbarkeit ist Teil des Designs, kein nachträglicher Kompromiss.

## Prinzip 3 — Effizienz vor Redundanz (EfficiencyScore)

Hardware- und Infrastrukturentscheidungen folgen einem gewichteten Multi-Kriterien-Score statt Einzelmetriken wie „mehr VRAM ist besser":

| Faktor | Gewicht | Bedeutung |
|---|---|---|
| `vram_per_eur` | 0.25 | Kapazität pro Investitionskosten |
| `vram_per_watt` | 0.15 | Energieeffizienz der Kapazität |
| `throughput_per_watt` | 0.15 | Effizienz-Proxy für Durchsatz |
| `software_maturity` | 0.15 | Reife des Software-Stacks (CUDA/ROCm) |
| `reliability` | 0.10 | = 1 − Maintenance-Risiko |
| `upgrade_path` | 0.10 | Skalierbarkeit (Single/Dual/Quad) |
| `maintenance_risk` | −0.05 | Straft riskante Konfigurationen |
| `complexity_penalty` | −0.05 | Straft operativen Multi-GPU-Overhead |

Der Score ist als Entscheidungshilfe für Infrastruktur-Teams gedacht, nicht als operativer KPI im Katalog — er bewertet Optionen vor der Entscheidung, KPIs bewerten den Betrieb danach.

## Prinzip 4 — Lifecycle-Denken statt Betriebsdenken

Embodied Carbon (Hardware-Herstellung, `HW-001`) und operationales CO₂ (`RUN-001/002`) werden gemeinsam betrachtet, nicht getrennt optimiert. Ein Design, das Betriebsemissionen senkt, aber häufigeren Hardware-Refresh erfordert, kann in Summe schlechter sein. Die Amortisierungsformel macht diesen Trade-off explizit:

```
EmbodiedCO2_per_request = EmbodiedCO2_hardware_kg × 1000 / (LifetimeMonths × RequestsPerMonth)
```

## Prinzip 5 — Proxy-Transparenz vor Präzisionsanschein

Ein proxybasierter Wert darf Hinweise geben, aber keine auditfähige Aussage ersetzen (siehe `GOV-002` Maturity-Level M0–M3). Datenquelle, Zeitpunkt und Proxy-Status werden mit jedem KPI-Wert mitgeführt, nicht nachträglich rekonstruiert.

## Prinzip 6 — Funktionale Einheit vor absoluten Zahlen

Vergleichbarkeit entsteht nur über eine fixierte funktionale Einheit. Build nutzt `R1` (1 CI/CD-Run), Run nutzt `R2a` (1 Service-Request), bis DHL eine geschäftsnähere Einheit bestätigt. Absolute CO₂-Zahlen ohne funktionale Einheit sind für Steuerungsentscheidungen wertlos.

## Prinzip 7 — Skalierungspfad einplanen

Multi-GPU-Cluster verlieren Effizienz durch `η_parallel` (empirisch 0.75–0.95). Design-Entscheidungen für Skalierung müssen diesen Verlust einpreisen, statt lineare Skalierung anzunehmen — sichtbar im `upgrade_path`-Faktor des EfficiencyScore und in der Kapazitätsbedingung des RDC-Operators (`docs/phase3_simulation_concept.md` §2).

## Zusammenspiel der Prinzipien

Green Gates (operative Schwellenwerte, Prinzip 2) und EfficiencyScore (Vorab-Entscheidungshilfe, Prinzip 3) ergänzen sich: Der EfficiencyScore hilft, bevor eine Konfiguration produktiv geht; die Green Gates überwachen, nachdem sie es ist. Phase 3 erweitert dieses Zusammenspiel um den RDC-Operator als dynamische Optimierung — die statischen Prinzipien hier bleiben dabei die normative Grundlage, nicht ihr Ersatz (`docs/phase3_simulation_concept.md` §7).
