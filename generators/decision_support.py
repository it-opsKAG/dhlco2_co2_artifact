"""Decision-support synthesis layer — the "letzte Verdichtungsschicht".

hardware_model.rdc_rank() and rdc_pareto.rdc_pareto_frontier() already compute real,
tested per-config metrics (CO2, cost, EfficiencyScore) and a Pareto frontier. What was
missing (see 2026-07-16 dashboard review) was the last step a decision-maker actually
asks for:

  1. One aggregated go/no-go gate status per candidate instead of only per-KPI zones
     (aggregate_gate_status) — a worst-of rule across the KPIs the simulation can
     actually compute (RUN-001, RUN-002, RUN-004; HW-001/HW-002 have no defined gate
     yet per data/green_gates.yaml and are excluded, not silently treated as passing).
  2. A ranking of which control variable ("Stellvariable") moves CO2 or cost the most
     for the chosen hardware — the "stärkster Hebel" from
     docs/phase3_simulation_concept.md §3, generalized from the single
     requests-per-month sensitivity already in rdc_pareto.py to all levers that are
     actually independent, workload/environment-level variables (not hardware choice
     itself, which is a different kind of decision).
  3. A single, auditable one-sentence recommendation (recommend_tier) — Pareto-optimal
     first, gate-compliant where possible, tie-broken by the model's own documented
     EfficiencyScore (docs/phase2_design_principles.md) — instead of only tables.

Deliberately does NOT invent a new weighted-sum "master score": Pareto dominance +
gate compliance + the existing EfficiencyScore are all already-documented, auditable
building blocks. Combining CO2 and cost into one artificial number would be exactly
the kind of false precision this repo avoids elsewhere (see green_gates.py's handling
of ordinal/undefined gates).
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from green_gates import gate_zone, has_defined_gate, load_green_gates
from hardware_model import EmissionFactorProfile, WorkloadProfile, rdc_rank
from rdc_pareto import rdc_pareto_frontier

# ---------------------------------------------------------------------------
# Aggregated Green-Gate status
# ---------------------------------------------------------------------------

# KPIs the simulation can compute a value for today. HW-001 (embodied CO2/request) and
# HW-002 (CAPEX/request) are deliberately excluded: both have threshold_basis: tbd in
# data/green_gates.yaml (awaiting hardware inventory / finance data), so including them
# would either silently pass them (wrong) or require inventing a threshold this repo
# hasn't earned yet (see docs/phase2_rdc_gap_analysis.md).
_GATE_ROW_FIELDS = (
    # (kpi_id, kpi_name, row_key_or_fn, unit)
    ("RUN-001", "Emissionen pro Transaktion",
     lambda row: row["hw001_embodied_gco2e_per_request"] + row["run_co2_gco2e_per_request"],
     "gCO2e/req"),
    ("RUN-002", "Energie pro Request", lambda row: row["run002_energy_wh_per_request"], "Wh/req"),
    ("RUN-004", "Energieproportionalität (Proxy)",
     lambda row: row["run004_energy_proportionality_ratio"], "ratio"),
)

_ZONE_ORDER = {"red": 3, "amber": 2, "green": 1}


@dataclass(frozen=True)
class GateContribution:
    kpi_id: str
    kpi_name: str
    value: float
    unit: str
    zone: str


@dataclass(frozen=True)
class AggregatedGateStatus:
    overall_zone: str  # green/amber/red/tbd
    contributions: list[GateContribution]


def aggregate_gate_status(
    row: dict, gates: Optional[dict] = None
) -> AggregatedGateStatus:
    """Worst-of aggregation across the KPIs computable from a rdc_rank() row.

    Rule: if any contributing KPI with a defined gate is red, overall is red; else if
    any is amber, overall is amber; else green. KPIs without a defined threshold
    ("tbd") never drag the result down and never count as a pass — they're excluded
    from the vote entirely. If none of the KPIs have a defined gate, overall is "tbd"
    rather than a fabricated "green" (would misrepresent an unevaluated case as safe).
    """
    gates = gates if gates is not None else load_green_gates()
    contributions = []
    for kpi_id, kpi_name, value_fn, unit in _GATE_ROW_FIELDS:
        value = value_fn(row)
        gate = gates.get(kpi_id)
        zone = gate_zone(value, gate) if has_defined_gate(gate) else "tbd"
        contributions.append(GateContribution(kpi_id, kpi_name, value, unit, zone))

    definitive = [c for c in contributions if c.zone in _ZONE_ORDER]
    overall = max(definitive, key=lambda c: _ZONE_ORDER[c.zone]).zone if definitive else "tbd"
    return AggregatedGateStatus(overall_zone=overall, contributions=contributions)


# ---------------------------------------------------------------------------
# Lever ranking — "stärkster Hebel" per docs/phase3_simulation_concept.md §3
# ---------------------------------------------------------------------------

# axis -> (label, "worse" value, "better" value). "Worse"/"better" are fixed per axis
# direction (e.g. more latency is always worse, more PV share is always better) so
# delta = worse_output - better_output is always >= 0 and reads as "achievable
# improvement", matching the "Stellhebel/Erkenntnis" framing already used in the
# presentation deck (Folie 8).
_AXIS_BOUNDS = {
    "requests_per_month": ("Nutzungsvolumen (Requests/Monat)", 1_000, 1_000_000),
    "pv_share": ("PV-/Ökostrom-Anteil", 0.0, 1.0),
    "grid_ef_gco2e_per_kwh": ("Strommix/Standort (Netz-Emissionsfaktor)", 485.0, 100.0),
    "avg_latency_s": ("Latenz/Verweildauer pro Request", 30.0, 1.0),
    "quality_score": ("Qualitätsanspruch", 0.7, 1.0),
}
# Bounds mirror generators/simulation_runner.py::SCENARIO_AXES so lever ranking stays
# consistent with the batch sweep's documented value ranges.

_CO2_LEVER_AXES = ("requests_per_month", "pv_share", "grid_ef_gco2e_per_kwh", "avg_latency_s")
# quality_score and grid_ef_gco2e_per_kwh are deliberately on only one of these two
# lists: quality_score has no CO2 effect in this model (it only scales
# cost_useful_outcome_eur's denominator — verified 2026-07-16), and the cost model has
# no carbon-price term, so grid_ef/pv_share have no cost effect. Omitting them here is
# the honest finding, not a gap to "fix" with a fabricated cross-term.
_COST_LEVER_AXES = ("requests_per_month", "avg_latency_s", "quality_score")


@dataclass(frozen=True)
class LeverImpact:
    axis: str
    axis_label: str
    worse_value: float
    better_value: float
    worse_output: float
    better_output: float
    delta: float  # worse_output - better_output; positive = achievable improvement


def _row_for(config_id: str, workload: WorkloadProfile, ef: EmissionFactorProfile) -> Optional[dict]:
    return next((r for r in rdc_rank(workload, ef) if r["id"] == config_id), None)


def _rank_levers(
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    config_id: str,
    axes: tuple[str, ...],
    output_fn,
) -> list[LeverImpact]:
    """One-at-a-time sensitivity: vary one axis to its documented bounds, hold the
    hardware config and every other axis at the scenario's actual value, rank by
    absolute impact on output_fn(row). None of these axes affect capacity_check(), so
    the same config_id remains feasible at both bounds."""
    impacts = []
    for axis in axes:
        label, worse, better = _AXIS_BOUNDS[axis]
        if axis in ("pv_share", "grid_ef_gco2e_per_kwh"):
            row_worse = _row_for(config_id, workload, replace(ef, **{axis: worse}))
            row_better = _row_for(config_id, workload, replace(ef, **{axis: better}))
        else:
            row_worse = _row_for(config_id, replace(workload, **{axis: worse}), ef)
            row_better = _row_for(config_id, replace(workload, **{axis: better}), ef)
        if row_worse is None or row_better is None:
            continue
        out_worse, out_better = output_fn(row_worse), output_fn(row_better)
        impacts.append(
            LeverImpact(axis, label, worse, better, out_worse, out_better, out_worse - out_better)
        )
    return sorted(impacts, key=lambda impact: abs(impact.delta), reverse=True)


def rank_co2_levers(
    workload: WorkloadProfile, ef: EmissionFactorProfile, config_id: str
) -> list[LeverImpact]:
    """Rank control variables by achievable CO2/request reduction, best-known config fixed."""
    return _rank_levers(
        workload, ef, config_id, _CO2_LEVER_AXES,
        lambda row: row["hw001_embodied_gco2e_per_request"] + row["run_co2_gco2e_per_request"],
    )


def rank_cost_levers(
    workload: WorkloadProfile, ef: EmissionFactorProfile, config_id: str
) -> list[LeverImpact]:
    """Rank control variables by achievable cost-per-useful-outcome reduction."""
    return _rank_levers(
        workload, ef, config_id, _COST_LEVER_AXES, lambda row: row["cost_useful_outcome_eur"]
    )


# ---------------------------------------------------------------------------
# Recommendation
# ---------------------------------------------------------------------------

_ZONE_WORDS = {
    "green": "grün — innerhalb der Ziel-Schwellenwerte",
    "amber": "gelb — Beobachtung empfohlen",
    "red": "rot — mindestens ein Ziel-Schwellenwert überschritten",
    "tbd": "ohne definierten Schwellenwert (siehe Green Gates)",
}


@dataclass(frozen=True)
class Recommendation:
    scenario_label: str
    config_id: str
    config_label: str
    total_co2_gco2e_per_request: float
    cost_useful_outcome_eur: float
    efficiency_score: float
    is_pareto_optimal: bool
    gate: AggregatedGateStatus
    all_candidates_red: bool
    rationale: str


def _build_rationale(
    scenario_label: str, row: dict, gate: AggregatedGateStatus, is_frontier: bool, all_red: bool
) -> str:
    co2 = row["hw001_embodied_gco2e_per_request"] + row["run_co2_gco2e_per_request"]
    cost = row["cost_useful_outcome_eur"]
    pareto_note = (
        "Pareto-optimal — keine machbare Konfiguration ist in CO2, Kosten und "
        "EfficiencyScore gleichzeitig besser."
        if is_frontier
        else "nicht auf der Pareto-Front, aber unter den gate-konformen Optionen die mit dem "
        "höchsten EfficiencyScore."
    )
    warning = (
        " Achtung: Für dieses Szenario ist jede machbare Konfiguration bei mindestens einem "
        "Green Gate rot — dies ist die am wenigsten kritische verfügbare Option, kein "
        "unproblematisches Ergebnis."
        if all_red
        else ""
    )
    return (
        f"{row['label']} ist für {scenario_label} die empfohlene Option: "
        f"{co2:.4f} gCO2e/Request, {cost:.4f} EUR/Request (Kosten je Nutzenoutput), "
        f"EfficiencyScore {row['efficiency_score']}. "
        f"Green-Gate-Status: {_ZONE_WORDS[gate.overall_zone]}. {pareto_note}{warning}"
    )


def recommend_tier(
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    scenario_label: str = "dieses Lastprofil",
) -> Optional[Recommendation]:
    """Pick one hardware config and generate an auditable, one-sentence rationale.

    Selection rule (in order): feasible (rdc_rank's own capacity/budget filters) ->
    prefer gate-compliant (overall_zone != red) -> prefer Pareto-optimal -> tie-break
    by EfficiencyScore (rdc_rank's own sort order, so pool[0] is already the winner).
    If every feasible candidate is gate-red, falls back to the full feasible pool
    rather than returning nothing — flagged via all_candidates_red so the caller must
    surface the warning, not hide the case.
    """
    ranked = rdc_rank(workload, ef)
    if not ranked:
        return None
    gates = load_green_gates()
    frontier_ids = {c.id for c in rdc_pareto_frontier(workload, ef)}

    evaluated = [(row, aggregate_gate_status(row, gates)) for row in ranked]
    non_red = [(row, gate) for row, gate in evaluated if gate.overall_zone != "red"]
    all_candidates_red = not non_red
    pool = non_red if non_red else evaluated

    pareto_in_pool = [(row, gate) for row, gate in pool if row["id"] in frontier_ids]
    # `pool` inherits rdc_rank()'s efficiency_score-descending order, so index 0 of
    # either list is already the correct tie-break winner without re-sorting.
    chosen_row, chosen_gate = pareto_in_pool[0] if pareto_in_pool else pool[0]
    is_frontier = chosen_row["id"] in frontier_ids

    return Recommendation(
        scenario_label=scenario_label,
        config_id=chosen_row["id"],
        config_label=chosen_row["label"],
        total_co2_gco2e_per_request=round(
            chosen_row["hw001_embodied_gco2e_per_request"] + chosen_row["run_co2_gco2e_per_request"], 6
        ),
        cost_useful_outcome_eur=chosen_row["cost_useful_outcome_eur"],
        efficiency_score=chosen_row["efficiency_score"],
        is_pareto_optimal=is_frontier,
        gate=chosen_gate,
        all_candidates_red=all_candidates_red,
        rationale=_build_rationale(scenario_label, chosen_row, chosen_gate, is_frontier, all_candidates_red),
    )


if __name__ == "__main__":
    from demo_scenarios import list_demo_scenarios

    for scenario in list_demo_scenarios():
        workload = scenario.to_workload()
        ef = scenario.to_emission_factor()
        rec = recommend_tier(workload, ef, scenario_label=scenario.name)
        print(f"=== {scenario.id} {scenario.name} ===")
        if rec is None:
            print("  Keine machbare Konfiguration.")
            continue
        print(f"  {rec.rationale}")
        top_config_id = rec.config_id
        levers = rank_co2_levers(workload, ef, top_config_id)
        if levers:
            top_lever = levers[0]
            print(
                f"  Stärkster CO2-Hebel: {top_lever.axis_label} "
                f"(Δ {top_lever.delta:.4f} gCO2e/req erreichbar)"
            )
        print()
