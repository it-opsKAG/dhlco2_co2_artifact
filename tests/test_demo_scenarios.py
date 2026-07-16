import pytest

from decision_support import recommend_tier
from demo_scenarios import (
    FUNCTION_AXIS_LABELS,
    VOLUME_AXIS_LABELS,
    coverage_summary,
    get_demo_scenario,
    list_demo_scenarios,
)
from hardware_model import rdc_rank


def test_list_demo_scenarios_returns_ten_unique_ids():
    scenarios = list_demo_scenarios()
    ids = [s.id for s in scenarios]
    assert len(ids) == 10
    assert len(set(ids)) == len(ids)


def test_coverage_matrix_doc_matches_yaml_ids_exactly():
    # Drift guard analogous to economic_intelligence_engine's coverage_report.py:
    # docs/demo_scenario_matrix.md must reference exactly the IDs that exist in
    # data/demo_scenarios.yaml, in both directions.
    summary = coverage_summary()
    assert summary["in_yaml_not_in_doc"] == set()
    assert summary["in_doc_not_in_yaml"] == set()


def test_non_edge_case_scenarios_use_documented_axis_codes():
    for scenario in list_demo_scenarios():
        if scenario.is_edge_case:
            assert scenario.function_axis is None
            assert scenario.volume_axis is None
        else:
            assert scenario.function_axis in FUNCTION_AXIS_LABELS
            assert scenario.volume_axis in VOLUME_AXIS_LABELS


def test_edge_case_scenarios_are_flagged():
    edge_cases = {s.id for s in list_demo_scenarios() if s.is_edge_case}
    assert edge_cases == {"DEMO-09", "DEMO-10"}


@pytest.mark.parametrize("scenario_id", [s.id for s in list_demo_scenarios()])
def test_each_scenario_has_at_least_one_feasible_hardware_config(scenario_id):
    scenario = get_demo_scenario(scenario_id)
    ranked = rdc_rank(scenario.to_workload(), scenario.to_emission_factor())
    assert ranked, f"{scenario_id} has no feasible hardware config"


@pytest.mark.parametrize("scenario_id", [s.id for s in list_demo_scenarios()])
def test_each_scenario_produces_a_recommendation_with_rationale(scenario_id):
    scenario = get_demo_scenario(scenario_id)
    rec = recommend_tier(
        scenario.to_workload(), scenario.to_emission_factor(), scenario_label=scenario.name
    )
    assert rec is not None
    assert rec.config_label
    assert scenario.name in rec.rationale
    assert rec.gate.overall_zone in {"green", "amber", "red", "tbd"}


def test_demo_02_chatbot_scenario_is_gate_green():
    # High volume + short latency amortizes embodied CO2 well — the dashboard's
    # default landing scenario should tell a "good news" story, not just the
    # worst case, or the library would be a governance demo with only bad news.
    scenario = get_demo_scenario("DEMO-02")
    rec = recommend_tier(scenario.to_workload(), scenario.to_emission_factor(), scenario.name)
    assert rec is not None
    assert rec.gate.overall_zone == "green"
    assert rec.all_candidates_red is False


def test_demo_10_worst_case_scenario_flags_all_candidates_red():
    # The one scenario deliberately designed to have no gate-compliant option —
    # the recommendation engine must surface this honestly, not hide it.
    scenario = get_demo_scenario("DEMO-10")
    assert scenario.is_edge_case is True
    rec = recommend_tier(scenario.to_workload(), scenario.to_emission_factor(), scenario.name)
    assert rec is not None
    assert rec.all_candidates_red is True
    assert rec.gate.overall_zone == "red"


def test_at_least_one_and_not_all_scenarios_are_gate_red():
    # Sanity check on the library as a whole: it should show a realistic mix, not
    # be uniformly green (which would mean the gates never bind) or uniformly red
    # (which would mean the "good news" scenarios don't exist).
    zones = []
    for scenario in list_demo_scenarios():
        rec = recommend_tier(scenario.to_workload(), scenario.to_emission_factor(), scenario.name)
        assert rec is not None
        zones.append(rec.gate.overall_zone)
    assert "green" in zones
    assert "red" in zones
