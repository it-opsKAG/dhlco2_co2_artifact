import pytest

from hardware_model import (
    EmissionFactorProfile,
    WorkloadProfile,
    _load_hardware_configs,
    rdc_rank,
    run002_energy_wh_per_request,
    run004_energy_proportionality_ratio,
    run_co2_per_request,
)


def _demo_workload(**overrides) -> WorkloadProfile:
    fields = dict(
        id="test-70b-q4",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
        quality_score=0.85,
        business_value_score=0.9,
    )
    fields.update(overrides)
    return WorkloadProfile(**fields)


def test_avg_latency_s_defaults_to_5_seconds():
    workload = _demo_workload()
    assert workload.avg_latency_s == 5.0


def test_rdc_rank_default_avg_latency_s_matches_explicit_5_seconds():
    # Regression guard: adding avg_latency_s to WorkloadProfile must not silently
    # change results for existing callers that never set it.
    ef = EmissionFactorProfile()
    implicit = rdc_rank(_demo_workload(), ef)
    explicit = rdc_rank(_demo_workload(avg_latency_s=5.0), ef)
    assert implicit == explicit


def test_avg_latency_s_scales_run_co2_linearly():
    ef = EmissionFactorProfile()
    slow = {r["id"]: r for r in rdc_rank(_demo_workload(avg_latency_s=30.0), ef)}
    fast = {r["id"]: r for r in rdc_rank(_demo_workload(avg_latency_s=1.0), ef)}
    for config_id, slow_row in slow.items():
        # run CO2 is energy(=power*latency) * emission factor -> linear in latency
        # (rel tolerance loosened slightly: both sides are independently rounded to
        # 6 decimals by rdc_rank(), so a x30 multiplication amplifies that rounding)
        assert slow_row["run_co2_gco2e_per_request"] == pytest.approx(
            fast[config_id]["run_co2_gco2e_per_request"] * 30.0, rel=1e-4
        )


def test_avg_latency_s_does_not_affect_embodied_co2():
    ef = EmissionFactorProfile()
    slow = {r["id"]: r for r in rdc_rank(_demo_workload(avg_latency_s=30.0), ef)}
    fast = {r["id"]: r for r in rdc_rank(_demo_workload(avg_latency_s=1.0), ef)}
    for config_id, slow_row in slow.items():
        assert slow_row["hw001_embodied_gco2e_per_request"] == fast[config_id][
            "hw001_embodied_gco2e_per_request"
        ]


def test_run002_energy_wh_per_request_matches_run_co2_formula():
    configs, _ = _load_hardware_configs()
    cfg = next(c for c in configs if c.id == "HW-CFG-T3-48GB")
    ef = EmissionFactorProfile(grid_ef_gco2e_per_kwh=485.0, pv_share=0.0)
    energy_wh = run002_energy_wh_per_request(cfg, avg_latency_s=5.0)
    dummy_workload = WorkloadProfile(
        id="x", model_size_b=0, quantization="generic", min_vram_gb=0, requests_per_month=1
    )
    run_co2 = run_co2_per_request(cfg, dummy_workload, ef, avg_latency_s=5.0)
    # run_co2 = (energy_wh/1000 kWh) * effective_ef(gCO2e/kWh); recompute the same way
    assert run_co2 == pytest.approx((energy_wh / 1000.0) * ef.effective_ef())


def test_run004_energy_proportionality_ratio_is_between_zero_and_one():
    configs, _ = _load_hardware_configs()
    for cfg in configs:
        ratio = run004_energy_proportionality_ratio(cfg)
        assert 0.0 <= ratio <= 1.0


def test_run004_energy_proportionality_ratio_matches_formula():
    configs, _ = _load_hardware_configs()
    cfg = next(c for c in configs if c.id == "HW-CFG-T1-16GB")
    expected = 1.0 - (cfg.power_idle_w / cfg.power_load_w)
    assert run004_energy_proportionality_ratio(cfg) == pytest.approx(expected)


def test_rdc_rank_rows_include_run002_and_run004_fields():
    ef = EmissionFactorProfile()
    ranked = rdc_rank(_demo_workload(), ef)
    assert ranked
    for row in ranked:
        assert "run002_energy_wh_per_request" in row
        assert "run004_energy_proportionality_ratio" in row
        assert row["run002_energy_wh_per_request"] > 0
