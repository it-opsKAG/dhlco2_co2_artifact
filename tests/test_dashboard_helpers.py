import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dashboard"))

from data_helpers import (
    build_pareto_rows,
    build_scenario_rows,
    build_sensitivity_rows,
    gate_zone,
    has_defined_gate,
    load_evidence_ledger_rows,
    load_green_gates,
    load_kpi_catalog,
)
from hardware_model import EmissionFactorProfile, WorkloadProfile


def _demo_workload():
    return WorkloadProfile(
        id="dashboard-test",
        model_size_b=70,
        quantization="Q4_K_M",
        min_vram_gb=48,
        requests_per_month=10_000,
        quality_score=0.9,
        business_value_score=0.9,
    )


def test_load_kpi_catalog_has_19_entries():
    kpis = load_kpi_catalog()
    assert len(kpis) == 19


def test_gate_zone_lower_is_better():
    gate = {"thresholds": {"green": {"max": 0.10}, "amber": {"max": 0.25}, "red": {"min": 0.25}}}
    assert gate_zone(0.05, gate) == "green"
    assert gate_zone(0.20, gate) == "amber"
    assert gate_zone(0.30, gate) == "red"


def test_gate_zone_higher_is_better():
    gate = {"thresholds": {"green": {"min": 0.70}, "amber": {"min": 0.40}, "red": {"max": 0.40}}}
    assert gate_zone(0.80, gate) == "green"
    assert gate_zone(0.50, gate) == "amber"
    assert gate_zone(0.20, gate) == "red"


def test_gate_zone_tbd_when_no_thresholds():
    gate = {"thresholds": {"green": {"max": None}, "amber": {"max": None}, "red": {"min": None}}}
    assert gate_zone(1.0, gate) == "tbd"


def test_gate_zone_tbd_for_ordinal_maturity_gate():
    # GOV-002-style gate: thresholds are "M0".."M3" strings, not numbers
    gate = {"thresholds": {"green": {"min": "M2"}, "amber": {"min": "M1"}, "red": {"max": "M0"}}}
    assert gate_zone(0, gate) == "tbd"
    assert has_defined_gate(gate) is True


def test_has_defined_gate_false_for_missing_or_tbd():
    assert has_defined_gate(None) is False
    assert has_defined_gate({"thresholds": {"green": {"max": None}}}) is False
    assert has_defined_gate({"thresholds": {"green": {"max": 0.1}}}) is True


def test_green_gates_cover_all_but_the_two_core_sci_kpis():
    # Verified 2026-07-15: SCI-001/SCI-002 (Core SCI group) have no entry in
    # data/green_gates.yaml — aggregate/boundary-dependent KPIs without an obvious
    # universal threshold. gate_zone() handles the missing-gate case as "tbd".
    gates = load_green_gates()
    kpis = load_kpi_catalog()
    kpi_ids = {kpi["id"] for kpi in kpis}
    missing = kpi_ids - gates.keys()
    assert missing == {"SCI-001", "SCI-002"}
    assert gate_zone(1.0, gates.get("SCI-001")) == "tbd"


def test_build_scenario_rows_nonempty_and_feasible():
    rows = build_scenario_rows(_demo_workload(), EmissionFactorProfile())
    assert len(rows) > 0
    for row in rows:
        assert row["VRAM eff. GB"] >= 48


def test_build_pareto_rows_frontier_is_subset():
    all_rows, frontier_labels = build_pareto_rows(_demo_workload(), EmissionFactorProfile())
    all_labels = {row["Config"] for row in all_rows}
    assert frontier_labels.issubset(all_labels)
    assert len(frontier_labels) > 0


def test_build_sensitivity_rows_matches_request_volume_count():
    workload = _demo_workload()
    ef = EmissionFactorProfile()
    top_config = build_scenario_rows(workload, ef)[0]
    # find the top config's underlying id via rdc_rank directly through pareto rows
    all_rows, _ = build_pareto_rows(workload, ef)
    config_id = None
    from hardware_model import rdc_rank

    for r in rdc_rank(workload, ef):
        if r["label"] == top_config["Config"]:
            config_id = r["id"]
            break
    assert config_id is not None

    rows = build_sensitivity_rows(workload, ef, config_id, [5_000, 10_000, 20_000])
    assert len(rows) == 2  # 3 volumes -> 2 ratio steps


def test_load_evidence_ledger_rows_returns_list():
    rows = load_evidence_ledger_rows()
    assert isinstance(rows, list)
