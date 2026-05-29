"""
Hardware CO2 and Cost Model — RDC-derived implementation.

Implements:
  - EfficiencyScore (Pareto-Bewertung je HardwareConfig)
  - CO2 Build (embodied amortization) per request
  - CO2 Run (energy * emission factor) per request
  - CostUsefulOutcome (CAPEX_ann + energy + maintenance) / UsefulOutputs
  - CapacityCheck (MemoryRequired <= EffectiveVRAM)
  - RDC stub: filter + rank hardware configs for a given workload

Consumed by: build_exports.py (optional hardware report), direct CLI use.
Data source: data/hardware_configs.yaml
"""

from __future__ import annotations

import csv
import io
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import yaml

_ROOT = Path(__file__).parent.parent
_HARDWARE_YAML = _ROOT / "data" / "hardware_configs.yaml"

# TDP-based embodied CO2 proxy: 0.5 kg CO2e per W of TDP
_EMBODIED_PROXY_KG_PER_W = 0.5


@dataclass
class HardwareConfig:
    id: str
    label: str
    gpu_type: str
    gpu_count: int
    vram_per_gpu_gb: float
    vram_effective_gb: float
    eta_parallel: float
    power_idle_w: float
    power_load_w: float
    capex_eur: float
    expected_lifetime_months: int
    maintenance_risk: float
    software_maturity: float
    embodied_co2_kg: Optional[float]
    embodied_co2_source: str
    notes: str = ""
    opex_eur_per_month: float = 0.0
    exclude_from_ranking: bool = False


@dataclass
class WorkloadProfile:
    id: str
    model_size_b: float
    quantization: str              # e.g. "INT4", "FP16", "Q4_K_M"
    min_vram_gb: float
    requests_per_month: int
    quality_score: float = 1.0     # 0.0–1.0
    business_value_score: float = 1.0  # 0.0–1.0


@dataclass
class EmissionFactorProfile:
    """Carbon intensity profile for the operating environment."""
    grid_ef_gco2e_per_kwh: float = 485.0   # German grid average (UBA 2024, gCO2e/kWh)
    pv_share: float = 0.0                   # fraction of consumption from on-site PV
    pv_ef_gco2e_per_kwh: float = 41.0      # LCA-based PV lifecycle emissions
    battery_share: float = 0.0
    battery_ef_gco2e_per_kwh: float = 60.0

    def effective_ef(self) -> float:
        """Blended emission factor (gCO2e/kWh) for the given energy mix."""
        grid_share = 1.0 - self.pv_share - self.battery_share
        return (
            self.pv_share * self.pv_ef_gco2e_per_kwh
            + self.battery_share * self.battery_ef_gco2e_per_kwh
            + grid_share * self.grid_ef_gco2e_per_kwh
        )


def _load_hardware_configs() -> tuple[list[HardwareConfig], dict]:
    raw = yaml.safe_load(_HARDWARE_YAML.read_text(encoding="utf-8"))
    configs = []
    for entry in raw.get("hardware_configs", []):
        configs.append(HardwareConfig(
            id=entry["id"],
            label=entry["label"],
            gpu_type=entry["gpu_type"],
            gpu_count=entry["gpu_count"],
            vram_per_gpu_gb=entry["vram_per_gpu_gb"],
            vram_effective_gb=entry["vram_effective_gb"],
            eta_parallel=entry["eta_parallel"],
            power_idle_w=entry["power_idle_w"],
            power_load_w=entry["power_load_w"],
            capex_eur=entry.get("capex_eur", 0.0),
            expected_lifetime_months=entry["expected_lifetime_months"],
            maintenance_risk=entry["maintenance_risk"],
            software_maturity=entry["software_maturity"],
            embodied_co2_kg=entry.get("embodied_co2_kg"),
            embodied_co2_source=entry.get("embodied_co2_source", "unknown"),
            notes=entry.get("notes", ""),
            opex_eur_per_month=entry.get("opex_eur_per_month", 0.0),
            exclude_from_ranking=entry.get("exclude_from_ranking", False),
        ))
    weights = raw.get("efficiency_score_weights", {})
    return configs, weights


def resolve_embodied_co2_kg(cfg: HardwareConfig) -> float:
    """Return embodied CO2 (kg) for the full cluster, using proxy if vendor value absent."""
    if cfg.embodied_co2_kg is not None:
        return cfg.embodied_co2_kg
    # Fallback: 0.5 kg CO2e per W TDP, summed over all GPUs
    return _EMBODIED_PROXY_KG_PER_W * cfg.power_load_w


def hw001_embodied_co2_per_request(
    cfg: HardwareConfig,
    workload: WorkloadProfile,
) -> float:
    """HW-001: Embodied CO2 per request (gCO2e/request).

    Formula: EmbodiedCO2_kg * 1000 / (LifetimeMonths * RequestsPerMonth)
    """
    embodied_kg = resolve_embodied_co2_kg(cfg)
    if cfg.expected_lifetime_months <= 0 or workload.requests_per_month <= 0:
        return float("inf")
    return (embodied_kg * 1000.0) / (cfg.expected_lifetime_months * workload.requests_per_month)


def hw002_capex_per_request(cfg: HardwareConfig, workload: WorkloadProfile) -> float:
    """HW-002: CAPEX amortized per request (EUR/request).

    Formula: (CAPEX_eur / LifetimeMonths) / RequestsPerMonth
    Cloud configs (capex=0) use opex_eur_per_month as denominator.
    """
    monthly_capex = (
        cfg.capex_eur / cfg.expected_lifetime_months
        if cfg.capex_eur > 0
        else cfg.opex_eur_per_month
    )
    if workload.requests_per_month <= 0:
        return float("inf")
    return monthly_capex / workload.requests_per_month


def run_co2_per_request(
    cfg: HardwareConfig,
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    avg_latency_s: float = 5.0,
) -> float:
    """RUN CO2 per request (gCO2e/request).

    Assumes GPU draws power_load_w during inference for avg_latency_s seconds.
    Formula: (Power_W * Latency_s / 3_600_000) * EF_gco2e_per_kWh
    """
    energy_kwh = cfg.power_load_w * avg_latency_s / 3_600_000.0
    return energy_kwh * ef.effective_ef()


def capacity_check(cfg: HardwareConfig, workload: WorkloadProfile) -> bool:
    """CapacityCheck: True if workload fits into effective VRAM."""
    return cfg.vram_effective_gb >= workload.min_vram_gb


def efficiency_score(cfg: HardwareConfig, weights: dict) -> float:
    """EfficiencyScore — weighted Pareto score for on-prem hardware selection.

    Uses total cost of ownership (CAPEX + monthly OPEX annualized) for VRAM/EUR.
    Cloud configs (capex_eur=0) use opex_eur_per_month * 12 as annual cost.
    exclude_from_ranking configs return -inf and should be filtered before calling.
    Higher score is better.
    """
    annual_cost = (
        cfg.capex_eur / (cfg.expected_lifetime_months / 12)
        if cfg.capex_eur > 0
        else cfg.opex_eur_per_month * 12
    )
    vram_per_eur = cfg.vram_effective_gb / max(annual_cost, 1)
    vram_per_watt = cfg.vram_effective_gb / max(cfg.power_load_w, 1)
    throughput_per_watt = cfg.vram_effective_gb / max(cfg.power_load_w, 1)
    reliability = 1.0 - cfg.maintenance_risk
    upgrade_path = {1: 0.5, 2: 0.7, 4: 0.6}.get(cfg.gpu_count, 0.4)
    complexity_penalty = {1: 0.0, 2: 0.1, 4: 0.2}.get(cfg.gpu_count, 0.3)

    raw = (
        weights.get("vram_per_eur", 0.25) * vram_per_eur * 1000  # scale: GB/kEUR/year
        + weights.get("vram_per_watt", 0.15) * vram_per_watt * 100
        + weights.get("throughput_per_watt", 0.15) * throughput_per_watt * 100
        + weights.get("software_maturity", 0.15) * cfg.software_maturity
        + weights.get("reliability", 0.10) * reliability
        + weights.get("upgrade_path", 0.10) * upgrade_path
        + weights.get("maintenance_risk", -0.05) * cfg.maintenance_risk
        + weights.get("complexity_penalty", -0.05) * complexity_penalty
    )
    return raw


def cost_useful_outcome(
    cfg: HardwareConfig,
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    avg_latency_s: float = 5.0,
    energy_cost_eur_per_kwh: float = 0.30,
) -> float:
    """EUR per useful output = (CAPEX_ann + EnergyCost + Maintenance) / UsefulOutputs.

    UsefulOutputs = RequestsPerMonth * QualityScore * BusinessValueScore
    """
    monthly_capex = (
        cfg.capex_eur / cfg.expected_lifetime_months
        if cfg.capex_eur > 0
        else cfg.opex_eur_per_month
    )
    energy_kwh_per_request = cfg.power_load_w * avg_latency_s / 3_600_000.0
    energy_cost_per_month = (
        energy_kwh_per_request * workload.requests_per_month * energy_cost_eur_per_kwh
    )
    maintenance_cost_per_month = monthly_capex * cfg.maintenance_risk * 0.1  # 10% of amortization
    total_cost_per_month = monthly_capex + energy_cost_per_month + maintenance_cost_per_month

    useful_outputs = (
        workload.requests_per_month
        * workload.quality_score
        * workload.business_value_score
    )
    if useful_outputs <= 0:
        return float("inf")
    return total_cost_per_month / useful_outputs


def rdc_rank(
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    budget_eur: float = float("inf"),
    co2_budget_gco2e_per_request: float = float("inf"),
) -> list[dict]:
    """Resource Decision Compiler — filter feasible configs, rank by EfficiencyScore.

    Returns: sorted list of dicts (highest score first), feasible configs only.
    """
    configs, weights = _load_hardware_configs()
    results = []
    for cfg in configs:
        if cfg.exclude_from_ranking:
            continue
        if not capacity_check(cfg, workload):
            continue
        if cfg.capex_eur > budget_eur:
            continue
        total_co2 = (
            hw001_embodied_co2_per_request(cfg, workload)
            + run_co2_per_request(cfg, workload, ef)
        )
        if total_co2 > co2_budget_gco2e_per_request:
            continue
        score = efficiency_score(cfg, weights)
        results.append({
            "id": cfg.id,
            "label": cfg.label,
            "vram_effective_gb": cfg.vram_effective_gb,
            "capex_eur": cfg.capex_eur,
            "efficiency_score": round(score, 4),
            "hw001_embodied_gco2e_per_request": round(
                hw001_embodied_co2_per_request(cfg, workload), 6
            ),
            "run_co2_gco2e_per_request": round(
                run_co2_per_request(cfg, workload, ef), 6
            ),
            "hw002_capex_eur_per_request": round(
                hw002_capex_per_request(cfg, workload), 6
            ),
            "cost_useful_outcome_eur": round(
                cost_useful_outcome(cfg, workload, ef), 4
            ),
        })
    return sorted(results, key=lambda x: x["efficiency_score"], reverse=True)


def render_hardware_report_md(workload: WorkloadProfile, ef: EmissionFactorProfile) -> str:
    """Generate a markdown report for a given workload + emission factor profile."""
    ranked = rdc_rank(workload, ef)
    lines = [
        "## Hardware Model Report",
        "",
        f"**Workload:** {workload.id} | {workload.model_size_b}B {workload.quantization} "
        f"| min VRAM {workload.min_vram_gb} GB | {workload.requests_per_month:,} req/month",
        f"**Emission Factor:** {ef.effective_ef():.1f} gCO₂e/kWh "
        f"(PV {ef.pv_share*100:.0f}%, Grid {(1-ef.pv_share-ef.battery_share)*100:.0f}%)",
        "",
        "| Config | VRAM eff. GB | CAPEX EUR | Eff.Score | Embodied gCO₂e/req | Run gCO₂e/req | EUR/req |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in ranked:
        lines.append(
            f"| {r['label']} | {r['vram_effective_gb']} | {r['capex_eur']:,.0f} "
            f"| {r['efficiency_score']} | {r['hw001_embodied_gco2e_per_request']:.4f} "
            f"| {r['run_co2_gco2e_per_request']:.4f} | {r['hw002_capex_eur_per_request']:.5f} |"
        )
    if not ranked:
        lines.append("| *No feasible config found* | | | | | | |")
    return "\n".join(lines)


def render_hardware_catalog_md() -> str:
    """Generate a hardware config catalog without a specific workload.

    Used by build_exports.py to produce Hardware_Model_Report.md.
    Shows all configs with static specs and EfficiencyScore (reference workload: 70B Q4, 10k req/mo).
    """
    configs, weights = _load_hardware_configs()
    ref_workload = WorkloadProfile(
        id="ref-70b-q4",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
    )
    ef_grid = EmissionFactorProfile()
    ef_pv = EmissionFactorProfile(pv_share=0.70, battery_share=0.10)

    lines = [
        "# Hardware Model Report",
        "",
        "Generated from `data/hardware_configs.yaml`. "
        "EfficiencyScore uses annualised TCO as cost denominator.",
        "",
        "**Reference workload for KPI columns:** 70B Q4_K_M, 10 000 req/month, "
        "5 s avg latency.",
        "",
        "## Hardware Configurations",
        "",
        "| ID | Label | GPUs | VRAM eff. GB | TDP W | CAPEX EUR | Lifetime mo | "
        "Maint. Risk | SW Maturity | Eff.Score | Excl. |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for cfg in configs:
        score = (
            "—"
            if cfg.exclude_from_ranking
            else str(round(efficiency_score(cfg, weights), 3))
        )
        lines.append(
            f"| {cfg.id} | {cfg.label} | {cfg.gpu_count} | {cfg.vram_effective_gb} "
            f"| {cfg.power_load_w} | {cfg.capex_eur:,.0f} | {cfg.expected_lifetime_months} "
            f"| {cfg.maintenance_risk} | {cfg.software_maturity} | {score} "
            f"| {'yes' if cfg.exclude_from_ranking else 'no'} |"
        )

    lines += [
        "",
        "## HW-001: Embodied CO2/Request (reference workload, proxy TDP method)",
        "",
        "| ID | Label | Embodied CO2 source | HW-001 gCO2e/req (grid) | HW-001 gCO2e/req (PV 70%) |",
        "|---|---|---|---|---|",
    ]
    for cfg in configs:
        emb_grid = round(hw001_embodied_co2_per_request(cfg, ref_workload), 5)
        run_grid = round(run_co2_per_request(cfg, ref_workload, ef_grid), 5)
        run_pv = round(run_co2_per_request(cfg, ref_workload, ef_pv), 5)
        lines.append(
            f"| {cfg.id} | {cfg.label} | {cfg.embodied_co2_source} "
            f"| {emb_grid + run_grid:.5f} | {emb_grid + run_pv:.5f} |"
        )

    lines += [
        "",
        "## HW-002: CAPEX/Request (reference workload)",
        "",
        "| ID | Label | CAPEX EUR | Lifetime mo | HW-002 EUR/req |",
        "|---|---|---|---|---|",
    ]
    for cfg in configs:
        cost = round(hw002_capex_per_request(cfg, ref_workload), 6)
        lines.append(
            f"| {cfg.id} | {cfg.label} | {cfg.capex_eur:,.0f} "
            f"| {cfg.expected_lifetime_months} | {cost:.6f} |"
        )

    lines += [
        "",
        "## Workload Capacity Map",
        "",
        "| Model Class | Min VRAM GB | Feasible Configs |",
        "|---|---|---|",
    ]
    raw = yaml.safe_load(_HARDWARE_YAML.read_text(encoding="utf-8"))
    for wc in raw.get("workload_capacity_map", []):
        feasible = [
            cfg.id for cfg in configs
            if cfg.vram_effective_gb >= wc["min_vram_gb"]
        ]
        lines.append(
            f"| {wc['label']} | {wc['min_vram_gb']} | {', '.join(feasible) or '—'} |"
        )

    return "\n".join(lines)


if __name__ == "__main__":
    # Quick smoke test / demo
    workload = WorkloadProfile(
        id="demo-70b-q4",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
        quality_score=0.85,
        business_value_score=0.9,
    )
    # Default: German grid average
    ef_grid = EmissionFactorProfile()
    # With PV (home server scenario)
    ef_pv = EmissionFactorProfile(pv_share=0.70, battery_share=0.10)

    print("=== Grid-only emission factor ===")
    print(render_hardware_report_md(workload, ef_grid))
    print()
    print("=== PV 70% / Battery 10% emission factor ===")
    print(render_hardware_report_md(workload, ef_pv))
