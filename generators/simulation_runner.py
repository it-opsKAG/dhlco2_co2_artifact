"""
Simulation Runner — parametrised scenario sweep over hardware configs.

Iterates over all combinations of Stellvariablen (control variables) and
runs rdc_rank() for each scenario. Outputs a CSV and a Markdown summary.

Usage:
  PYTHONUTF8=1 python generators/simulation_runner.py
  PYTHONUTF8=1 python generators/simulation_runner.py --output-dir exports/

Extend the SCENARIO_AXES dict below to add or change sweep dimensions.
"""

from __future__ import annotations

import csv
import itertools
import sys
from pathlib import Path
from typing import Any

# Make generators/ importable when run directly
sys.path.insert(0, str(Path(__file__).parent))

from hardware_model import (
    EmissionFactorProfile,
    WorkloadProfile,
    cost_useful_outcome,
    hw001_embodied_co2_per_request,
    hw002_capex_per_request,
    run_co2_per_request,
    capacity_check,
    efficiency_score,
    _load_hardware_configs,
)


# ---------------------------------------------------------------------------
# Stellvariablen — control variable axes for the scenario sweep.
# Each key maps to a list of values to iterate over.
# Add, remove, or adjust values to shape the simulation scope.
# ---------------------------------------------------------------------------
SCENARIO_AXES: dict[str, list[Any]] = {
    # Workload: minimum VRAM requirement (GB) — proxy for model size / quantization
    "min_vram_gb": [16, 24, 48, 96],

    # Workload: monthly request volume
    "requests_per_month": [1_000, 10_000, 100_000, 1_000_000],

    # Emission factor profile: PV share (0.0 = pure grid, 1.0 = pure solar)
    "pv_share": [0.0, 0.30, 0.70, 1.0],

    # Emission factor: grid emission factor (gCO2e/kWh)
    # DE avg 2024 = 485; EU avg ≈ 295; green-energy target ≈ 50
    "grid_ef_gco2e_per_kwh": [485, 295, 100],

    # Workload: average inference/request latency (seconds) — drives RUN CO2
    # (energy = power_load_w * avg_latency_s), TASK-05
    "avg_latency_s": [1.0, 5.0, 30.0],

    # Workload: output quality weight (0.0-1.0) — drives cost_useful_outcome,
    # TASK-05. Business value score stays fixed (see _BUSINESS_VALUE_SCORE);
    # only quality is swept to keep the scenario count manageable.
    "quality_score": [0.7, 0.85, 1.0],
}

# Fixed parameters (not swept) — change here or pass programmatically
_BUSINESS_VALUE_SCORE: float = 1.0  # business value weight (0.0–1.0)


def _build_scenarios() -> list[dict[str, Any]]:
    """Return all Cartesian-product combinations of SCENARIO_AXES."""
    keys = list(SCENARIO_AXES.keys())
    values = list(SCENARIO_AXES.values())
    return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


def run_simulation(output_dir: Path | None = None) -> list[dict[str, Any]]:
    """Run the full scenario sweep.

    Returns a flat list of result dicts (one row per hardware config per scenario).
    Writes simulation_results.csv and simulation_summary.md to output_dir.
    """
    configs, weights = _load_hardware_configs()
    scenarios = _build_scenarios()

    rows: list[dict[str, Any]] = []

    for sc in scenarios:
        workload = WorkloadProfile(
            id=f"sim_vram{sc['min_vram_gb']}_req{sc['requests_per_month']}",
            model_size_b=0,          # not used by capacity_check or CO2 calc
            quantization="generic",
            min_vram_gb=sc["min_vram_gb"],
            requests_per_month=sc["requests_per_month"],
            quality_score=sc["quality_score"],
            business_value_score=_BUSINESS_VALUE_SCORE,
        )
        ef = EmissionFactorProfile(
            pv_share=sc["pv_share"],
            grid_ef_gco2e_per_kwh=sc["grid_ef_gco2e_per_kwh"],
        )
        avg_latency_s = sc["avg_latency_s"]

        for cfg in configs:
            if cfg.exclude_from_ranking:
                continue
            if not capacity_check(cfg, workload):
                continue

            embodied = hw001_embodied_co2_per_request(cfg, workload)
            run_co2 = run_co2_per_request(cfg, workload, ef, avg_latency_s)
            total_co2 = embodied + run_co2
            capex_per_req = hw002_capex_per_request(cfg, workload)
            eff_score = efficiency_score(cfg, weights)
            ef_blend = ef.effective_ef()
            cost_per_useful_output = cost_useful_outcome(cfg, workload, ef, avg_latency_s)

            rows.append({
                # Scenario axes
                "sc_min_vram_gb": sc["min_vram_gb"],
                "sc_requests_per_month": sc["requests_per_month"],
                "sc_pv_share": sc["pv_share"],
                "sc_grid_ef_gco2e_per_kwh": sc["grid_ef_gco2e_per_kwh"],
                "sc_avg_latency_s": avg_latency_s,
                "sc_quality_score": sc["quality_score"],
                "sc_blended_ef_gco2e_per_kwh": round(ef_blend, 2),
                # Hardware config
                "hw_id": cfg.id,
                "hw_label": cfg.label,
                "hw_vram_effective_gb": cfg.vram_effective_gb,
                "hw_gpu_count": cfg.gpu_count,
                "hw_power_load_w": cfg.power_load_w,
                "hw_capex_eur": cfg.capex_eur,
                "hw_lifetime_months": cfg.expected_lifetime_months,
                "hw_maintenance_risk": cfg.maintenance_risk,
                # KPI results
                "hw001_embodied_gco2e_per_req": round(embodied, 6),
                "run_co2_gco2e_per_req": round(run_co2, 6),
                "total_co2_gco2e_per_req": round(total_co2, 6),
                "hw002_capex_eur_per_req": round(capex_per_req, 6),
                "efficiency_score": round(eff_score, 4),
                "cost_useful_outcome_eur": round(cost_per_useful_output, 6),
            })

    if output_dir is not None:
        _write_csv(rows, output_dir / "simulation_results.csv")
        _write_summary_md(rows, scenarios, output_dir / "simulation_summary.md")

    return rows


def _write_csv(rows: list[dict], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {len(rows):,} rows → {path}")


def _write_summary_md(
    rows: list[dict],
    scenarios: list[dict],
    path: Path,
) -> None:
    """Write a human-readable summary: best config per scenario (highest eff. score)."""
    from collections import defaultdict

    # Group by scenario key, find best config per scenario
    sc_keys = ("sc_min_vram_gb", "sc_requests_per_month", "sc_pv_share",
               "sc_grid_ef_gco2e_per_kwh")
    best: dict[tuple, dict] = {}
    for row in rows:
        key = tuple(row[k] for k in sc_keys)
        if key not in best or row["efficiency_score"] > best[key]["efficiency_score"]:
            best[key] = row

    lines = [
        "# Simulation Summary",
        "",
        f"**Scenarios total:** {len(scenarios)}  "
        f"**Result rows:** {len(rows)}  "
        f"**Unique scenario × config combinations:** {len(rows)}",
        "",
        "## Best Config per Scenario (highest EfficiencyScore, feasibility-filtered)",
        "",
        "| VRAM req GB | Req/mo | PV share | Grid EF gCO₂e/kWh | Best config | "
        "Eff.Score | Total CO₂ gCO₂e/req | EUR/req |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for key in sorted(best.keys()):
        r = best[key]
        lines.append(
            f"| {r['sc_min_vram_gb']} | {r['sc_requests_per_month']:,} "
            f"| {r['sc_pv_share']:.0%} | {r['sc_grid_ef_gco2e_per_kwh']} "
            f"| {r['hw_label']} | {r['efficiency_score']} "
            f"| {r['total_co2_gco2e_per_req']:.5f} | {r['hw002_capex_eur_per_req']:.5f} |"
        )

    # CO2 sensitivity: compare grid vs PV 70% for most common config
    lines += [
        "",
        "## CO₂ Sensitivity: Grid-only vs PV 70%",
        "",
        "Shows how PV share changes total CO₂/request for each hardware tier at 10k req/mo.",
        "",
        "| Config | VRAM GB | Grid CO₂ gCO₂e/req | PV 70% CO₂ gCO₂e/req | Δ reduction |",
        "|---|---|---|---|---|",
    ]
    grid_rows = {r["hw_id"]: r for r in rows
                 if r["sc_pv_share"] == 0.0
                 and r["sc_requests_per_month"] == 10_000
                 and r["sc_grid_ef_gco2e_per_kwh"] == 485
                 and r["sc_min_vram_gb"] == 48}
    pv_rows = {r["hw_id"]: r for r in rows
               if r["sc_pv_share"] == 0.70
               and r["sc_requests_per_month"] == 10_000
               and r["sc_grid_ef_gco2e_per_kwh"] == 485
               and r["sc_min_vram_gb"] == 48}
    for hw_id, gr in sorted(grid_rows.items()):
        if hw_id in pv_rows:
            pr = pv_rows[hw_id]
            delta = (gr["total_co2_gco2e_per_req"] - pr["total_co2_gco2e_per_req"])
            pct = delta / gr["total_co2_gco2e_per_req"] * 100 if gr["total_co2_gco2e_per_req"] else 0
            lines.append(
                f"| {gr['hw_label']} | {gr['hw_vram_effective_gb']} "
                f"| {gr['total_co2_gco2e_per_req']:.5f} "
                f"| {pr['total_co2_gco2e_per_req']:.5f} "
                f"| -{pct:.1f}% |"
            )

    lines += ["", f"*Generated by simulation_runner.py — {len(scenarios)} scenarios × "
              f"{len({r['hw_id'] for r in rows})} feasible configs*"]

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  wrote summary → {path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run CO2 simulation sweep")
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).parent.parent / "exports"),
        help="Directory to write simulation_results.csv and simulation_summary.md",
    )
    args = parser.parse_args()
    output_dir = Path(args.output_dir)

    print(f"Running simulation: {len(_build_scenarios())} scenarios...")
    results = run_simulation(output_dir=output_dir)
    print(f"Done. {len(results):,} result rows written to {output_dir}")
