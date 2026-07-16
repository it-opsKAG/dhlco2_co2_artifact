import pytest

from decision_support import (
    aggregate_gate_status,
    rank_co2_levers,
    rank_cost_levers,
    recommend_tier,
)
from hardware_model import EmissionFactorProfile, WorkloadProfile, rdc_rank


def _row(total_co2: float, energy_wh: float, proportionality: float) -> dict:
    """Hand-crafted rdc_rank()-shaped row for deterministic gate-aggregation tests."""
    return {
        "hw001_embodied_gco2e_per_request": total_co2 / 2,
        "run_co2_gco2e_per_request": total_co2 / 2,
        "run002_energy_wh_per_request": energy_wh,
        "run004_energy_proportionality_ratio": proportionality,
    }


def _demo_workload(**overrides) -> WorkloadProfile:
    fields = dict(
        id="ds-test",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
        quality_score=0.85,
        business_value_score=0.9,
    )
    fields.update(overrides)
    return WorkloadProfile(**fields)


# ---------------------------------------------------------------------------
# aggregate_gate_status — worst-of rule
# ---------------------------------------------------------------------------


def test_aggregate_gate_status_all_green():
    gate = aggregate_gate_status(_row(total_co2=0.05, energy_wh=0.1, proportionality=0.9))
    assert gate.overall_zone == "green"


def test_aggregate_gate_status_worst_of_picks_red_even_if_others_green():
    # RUN-001 red (total_co2=1.0 > 0.25), RUN-002/RUN-004 green
    gate = aggregate_gate_status(_row(total_co2=1.0, energy_wh=0.1, proportionality=0.9))
    assert gate.overall_zone == "red"
    run001 = next(c for c in gate.contributions if c.kpi_id == "RUN-001")
    assert run001.zone == "red"


def test_aggregate_gate_status_amber_when_worst_is_amber():
    # RUN-001 amber (0.10 < 0.20 <= 0.25), others green
    gate = aggregate_gate_status(_row(total_co2=0.20, energy_wh=0.1, proportionality=0.9))
    assert gate.overall_zone == "amber"


def test_aggregate_gate_status_only_considers_run_001_002_004():
    # HW-001/HW-002 have no defined gate (threshold_basis: tbd) and must not appear.
    gate = aggregate_gate_status(_row(total_co2=0.05, energy_wh=0.1, proportionality=0.9))
    assert {c.kpi_id for c in gate.contributions} == {"RUN-001", "RUN-002", "RUN-004"}


# ---------------------------------------------------------------------------
# Lever ranking
# ---------------------------------------------------------------------------


def test_rank_co2_levers_excludes_quality_score():
    # quality_score has no effect on CO2 in this model (verified 2026-07-16) — it must
    # not appear in the CO2 lever ranking at all, rather than showing a fake zero delta.
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    config_id = rdc_rank(workload, ef)[0]["id"]
    levers = rank_co2_levers(workload, ef, config_id)
    axes = {lever.axis for lever in levers}
    assert "quality_score" not in axes
    assert "grid_ef_gco2e_per_kwh" in axes
    assert "requests_per_month" in axes


def test_rank_co2_levers_sorted_descending_by_remaining_headroom():
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    config_id = rdc_rank(workload, ef)[0]["id"]
    levers = rank_co2_levers(workload, ef, config_id)
    assert levers
    deltas = [lever.delta for lever in levers]
    assert deltas == sorted(deltas, reverse=True)
    for lever in levers:
        # delta is remaining improvement from the current value, clamped at 0
        assert lever.delta >= 0


def test_rank_co2_levers_is_scenario_sensitive():
    # Regression for the 2026-07-16 audit finding: with fixed worse->best bounds the
    # ranking showed "requests_per_month, delta 7.98" as top lever for EVERY scenario —
    # including ones already at 1M requests. Headroom must be measured from the
    # scenario's CURRENT values: a scenario already at best volume and best latency has
    # zero remaining headroom on those axes, and its top lever must be an energy-mix
    # axis instead.
    workload = _demo_workload(requests_per_month=1_000_000, avg_latency_s=1.0)
    ef = EmissionFactorProfile(grid_ef_gco2e_per_kwh=295.0, pv_share=0.30)
    config_id = rdc_rank(workload, ef)[0]["id"]
    levers = {lever.axis: lever for lever in rank_co2_levers(workload, ef, config_id)}

    assert levers["requests_per_month"].delta == 0.0
    assert levers["avg_latency_s"].delta == 0.0
    top_axis = max(levers.values(), key=lambda lever: lever.delta).axis
    assert top_axis in ("pv_share", "grid_ef_gco2e_per_kwh")


def test_rank_co2_levers_clamps_beyond_best_values_to_zero():
    # A scenario BEYOND the model's best sweep value (e.g. 5M requests > 1M bound,
    # 0.5s latency < 1.0s bound) must show zero remaining headroom, not a negative
    # or fabricated positive delta.
    workload = _demo_workload(requests_per_month=5_000_000, avg_latency_s=0.5)
    ef = EmissionFactorProfile()
    config_id = rdc_rank(workload, ef)[0]["id"]
    levers = {lever.axis: lever for lever in rank_co2_levers(workload, ef, config_id)}
    assert levers["requests_per_month"].delta == 0.0
    assert levers["avg_latency_s"].delta == 0.0


def test_rank_cost_levers_excludes_grid_ef_and_pv_share():
    # The cost model has no carbon-price term — grid_ef/pv_share cannot affect it.
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    config_id = rdc_rank(workload, ef)[0]["id"]
    levers = rank_cost_levers(workload, ef, config_id)
    axes = {lever.axis for lever in levers}
    assert "grid_ef_gco2e_per_kwh" not in axes
    assert "pv_share" not in axes
    assert "quality_score" in axes


def test_rank_cost_levers_quality_score_delta_is_positive():
    # Higher quality_score -> more useful outputs -> lower cost per useful outcome.
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    config_id = rdc_rank(workload, ef)[0]["id"]
    levers = rank_cost_levers(workload, ef, config_id)
    quality_lever = next(lever for lever in levers if lever.axis == "quality_score")
    assert quality_lever.delta > 0


# ---------------------------------------------------------------------------
# recommend_tier
# ---------------------------------------------------------------------------


def test_recommend_tier_none_when_infeasible():
    workload = _demo_workload(min_vram_gb=10_000)  # no tier has this much VRAM
    ef = EmissionFactorProfile()
    assert recommend_tier(workload, ef) is None


def test_recommend_tier_green_high_volume_realtime_scenario():
    # Mirrors DEMO-02 (Sendungsverfolgung-Chatbot): high volume + short latency
    # amortizes embodied CO2 well enough to clear RUN-001's green threshold —
    # verified via generators/decision_support.py's own __main__ demo run.
    workload = _demo_workload(
        min_vram_gb=24, requests_per_month=1_000_000, avg_latency_s=1.0,
        quality_score=0.85, business_value_score=0.90,
    )
    ef = EmissionFactorProfile(grid_ef_gco2e_per_kwh=295, pv_share=0.30)
    rec = recommend_tier(workload, ef, scenario_label="Testszenario")
    assert rec is not None
    assert rec.config_label
    assert "Testszenario" in rec.rationale
    assert rec.gate.overall_zone == "green"
    assert rec.is_pareto_optimal is True
    assert rec.all_candidates_red is False


def test_recommend_tier_flags_all_candidates_red_worst_case():
    # Mirrors DEMO-10 (Worst-Case: Altbestand ohne Ökostrom): large model, no PV,
    # high latency, DE grid average — every feasible tier is RUN-001/002-red.
    workload = _demo_workload(
        min_vram_gb=96, requests_per_month=1_000, avg_latency_s=30.0,
        quality_score=0.7, business_value_score=0.7,
    )
    ef = EmissionFactorProfile(grid_ef_gco2e_per_kwh=485.0, pv_share=0.0)
    rec = recommend_tier(workload, ef, scenario_label="Worst-Case-Test")
    assert rec is not None
    assert rec.all_candidates_red is True
    assert rec.gate.overall_zone == "red"
    assert "Achtung" in rec.rationale


def test_recommend_tier_gate_zone_is_always_one_of_four_values():
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    rec = recommend_tier(workload, ef)
    assert rec is not None
    assert rec.gate.overall_zone in {"green", "amber", "red", "tbd"}
