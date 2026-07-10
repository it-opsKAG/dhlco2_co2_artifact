"""Phase-3 first step: turn rdc_rank()'s per-config metrics into a real Pareto frontier.

rdc_rank() (hardware_model.py) already computes, per feasible HardwareConfig:
  efficiency_score, hw001_embodied_gco2e_per_request, run_co2_gco2e_per_request,
  hw002_capex_eur_per_request, cost_useful_outcome_eur
but only ever ranks by the single efficiency_score dimension. This module treats
CO2/request, EUR/request and EfficiencyScore as independent Pareto dimensions instead,
and adds sensitivity analysis over a workload control variable — the ParetoOptimizer
and sensitivity steps described in docs/phase3_simulation_concept.md section 3.

Uses adaptive_decision_kernel.optimization (shared, domain-agnostic) rather than a
DHL-local Pareto implementation, so a second, non-DHL pilot can reuse the same code.
"""

from __future__ import annotations

from dataclasses import replace

from adaptive_decision_kernel.optimization import (
    Candidate,
    Dimension,
    SensitivityPoint,
    SensitivityStep,
    pareto_frontier,
    sensitivity_ratios,
)
from hardware_model import EmissionFactorProfile, WorkloadProfile, rdc_rank

PARETO_DIMENSIONS = [
    Dimension(id="total_co2_gco2e_per_request", goal="minimize"),
    Dimension(id="cost_useful_outcome_eur", goal="minimize"),
    Dimension(id="efficiency_score", goal="maximize"),
]


def rdc_pareto_frontier(
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    budget_eur: float = float("inf"),
    co2_budget_gco2e_per_request: float = float("inf"),
) -> list[Candidate]:
    """Rank-and-filter via rdc_rank(), then reduce to the Pareto-optimal subset.

    Replaces single-objective sorting with a real multi-objective comparison across
    CO2/request, EUR/request and EfficiencyScore.
    """
    ranked = rdc_rank(workload, ef, budget_eur, co2_budget_gco2e_per_request)
    candidates = [
        Candidate(
            id=row["id"],
            values={
                "total_co2_gco2e_per_request": (
                    row["hw001_embodied_gco2e_per_request"] + row["run_co2_gco2e_per_request"]
                ),
                "cost_useful_outcome_eur": row["cost_useful_outcome_eur"],
                "efficiency_score": row["efficiency_score"],
            },
            metadata={"label": row["label"], "capex_eur": row["capex_eur"]},
        )
        for row in ranked
    ]
    return pareto_frontier(candidates, PARETO_DIMENSIONS)


def co2_sensitivity_to_requests_per_month(
    base_workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    config_id: str,
    request_volumes: list[int],
) -> list[SensitivityStep]:
    """Delta(total CO2/request) per Delta(requests_per_month) for one fixed hardware config.

    Varies the requests_per_month workload control variable while holding hardware
    fixed — the "Sensitivitaetsanalyse: Delta_co2 / Delta_Stellvariable" step from
    docs/phase3_simulation_concept.md section 3.
    """
    samples: list[SensitivityPoint] = []
    for volume in request_volumes:
        workload = replace(base_workload, requests_per_month=volume)
        row = next((r for r in rdc_rank(workload, ef) if r["id"] == config_id), None)
        if row is None:
            continue
        total_co2 = row["hw001_embodied_gco2e_per_request"] + row["run_co2_gco2e_per_request"]
        samples.append(SensitivityPoint(input_value=float(volume), output_value=total_co2))
    return sensitivity_ratios(samples)


if __name__ == "__main__":
    demo_workload = WorkloadProfile(
        id="demo-70b-q4",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
        quality_score=0.85,
        business_value_score=0.9,
    )
    demo_ef = EmissionFactorProfile()

    frontier = rdc_pareto_frontier(demo_workload, demo_ef)
    print(f"=== Pareto frontier ({len(frontier)} of {len(rdc_rank(demo_workload, demo_ef))} feasible configs) ===")
    for candidate in frontier:
        print(f"  {candidate.metadata['label']}: {candidate.values}")

    print()
    print("=== CO2 sensitivity to requests_per_month (top config) ===")
    top_id = rdc_rank(demo_workload, demo_ef)[0]["id"]
    for step in co2_sensitivity_to_requests_per_month(
        demo_workload, demo_ef, top_id, [5_000, 10_000, 20_000, 40_000]
    ):
        print(f"  {step.from_input:>7.0f} -> {step.to_input:>7.0f} req/mo: ratio={step.ratio:.6f} gCO2e/req per req/mo")
