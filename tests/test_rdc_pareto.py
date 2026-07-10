from hardware_model import EmissionFactorProfile, WorkloadProfile, rdc_rank
from rdc_pareto import co2_sensitivity_to_requests_per_month, rdc_pareto_frontier


def _demo_workload() -> WorkloadProfile:
    return WorkloadProfile(
        id="test-70b-q4",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
        quality_score=0.85,
        business_value_score=0.9,
    )


def test_pareto_frontier_is_nonempty_and_subset_of_ranked() -> None:
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    ranked_ids = {row["id"] for row in rdc_rank(workload, ef)}
    frontier = rdc_pareto_frontier(workload, ef)
    assert frontier, "Pareto frontier should not be empty for a feasible workload"
    assert {c.id for c in frontier}.issubset(ranked_ids)


def test_top_efficiency_score_config_is_always_on_the_frontier() -> None:
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    ranked = rdc_rank(workload, ef)
    top_by_efficiency = ranked[0]["id"]
    frontier_ids = {c.id for c in rdc_pareto_frontier(workload, ef)}
    assert top_by_efficiency in frontier_ids


def test_frontier_shrinks_under_tighter_co2_budget() -> None:
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    loose = rdc_pareto_frontier(workload, ef)
    tight = rdc_pareto_frontier(workload, ef, co2_budget_gco2e_per_request=0.001)
    assert len(tight) <= len(loose)


def test_co2_sensitivity_to_request_volume_is_negative_due_to_amortization() -> None:
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    ranked = rdc_rank(workload, ef)
    config_id = ranked[0]["id"]
    steps = co2_sensitivity_to_requests_per_month(
        workload, ef, config_id, request_volumes=[5_000, 10_000, 20_000]
    )
    assert len(steps) == 2
    assert all(step.ratio is not None and step.ratio < 0 for step in steps)
