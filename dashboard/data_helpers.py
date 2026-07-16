"""Pure data-shaping helpers for the Streamlit dashboard — no Streamlit import here.

Kept separate from app.py so the logic is unit-testable without a Streamlit runtime.
Reads the same SSOT data files and generator modules the CI export pipeline uses;
no mocked or invented numbers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
GENERATORS_DIR = ROOT / "generators"
if str(GENERATORS_DIR) not in sys.path:
    sys.path.insert(0, str(GENERATORS_DIR))

from decision_support import (  # noqa: E402
    AggregatedGateStatus,
    Recommendation,
    aggregate_gate_status,
    rank_co2_levers,
    rank_cost_levers,
    recommend_tier,
)
from demo_scenarios import DemoScenario, list_demo_scenarios  # noqa: E402
from green_gates import (  # noqa: E402  (re-exported for existing importers of data_helpers)
    ZONE_EMOJI,
    gate_zone,
    has_defined_gate,
    load_green_gates,
)
from hardware_model import (  # noqa: E402
    EmissionFactorProfile,
    WorkloadProfile,
    rdc_rank,
)
from rdc_pareto import (  # noqa: E402
    co2_sensitivity_to_requests_per_month,
    rdc_pareto_frontier,
)

DATA_DIR = ROOT / "data"
EVIDENCE_LEDGER_JSONL = ROOT / "evidence" / "simulation_runs.jsonl"
CROSS_REPO_BENCHMARK_YAML = ROOT / "evidence" / "cross_repo_benchmark.yaml"


def load_kpi_catalog() -> list[dict[str, Any]]:
    doc = yaml.safe_load((DATA_DIR / "kpis.yaml").read_text(encoding="utf-8"))
    return list(doc.get("kpis", []))


def build_scenario_rows(
    workload: WorkloadProfile, ef: EmissionFactorProfile
) -> list[dict[str, Any]]:
    """Hardware comparison rows for the current sidebar scenario (feasible configs only)."""
    ranked = rdc_rank(workload, ef)
    rows = []
    for r in ranked:
        gate = aggregate_gate_status(r)
        rows.append(
            {
                "Config": r["label"],
                "VRAM eff. GB": r["vram_effective_gb"],
                "EfficiencyScore": r["efficiency_score"],
                "Embodied gCO2e/req": r["hw001_embodied_gco2e_per_request"],
                "Run gCO2e/req": r["run_co2_gco2e_per_request"],
                "Total gCO2e/req": round(
                    r["hw001_embodied_gco2e_per_request"] + r["run_co2_gco2e_per_request"], 6
                ),
                "EUR/req": r["hw002_capex_eur_per_request"],
                "Gate (RUN-001/002/004)": f"{ZONE_EMOJI.get(gate.overall_zone, '⚪')} {gate.overall_zone}",
            }
        )
    return rows


def build_pareto_rows(
    workload: WorkloadProfile, ef: EmissionFactorProfile
) -> tuple[list[dict[str, Any]], set[str]]:
    """All feasible configs plus the subset of IDs on the Pareto-optimal frontier."""
    all_rows = build_scenario_rows(workload, ef)
    frontier = rdc_pareto_frontier(workload, ef)
    frontier_labels = {c.metadata["label"] for c in frontier}
    return all_rows, frontier_labels


def build_sensitivity_rows(
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    config_id: str,
    request_volumes: list[int],
) -> list[dict[str, Any]]:
    steps = co2_sensitivity_to_requests_per_month(workload, ef, config_id, request_volumes)
    return [
        {
            "Von Req/Monat": int(step.from_input),
            "Zu Req/Monat": int(step.to_input),
            "Ratio (gCO2e/Req je Req/Monat)": step.ratio,
        }
        for step in steps
    ]


def load_evidence_ledger_rows() -> list[dict[str, Any]]:
    if not EVIDENCE_LEDGER_JSONL.exists():
        return []
    rows = []
    for line in EVIDENCE_LEDGER_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        rows.append(
            {
                "Run ID": entry.get("run_id"),
                "Erstellt (UTC)": entry.get("created_at"),
                "Git-Commit": str(entry.get("git_commit", ""))[:12],
                "Szenarien": entry.get("scenario_count"),
                "Zeilen": entry.get("result_row_count"),
                "CSV SHA-256 (kurz)": entry.get("outputs", {})
                .get("simulation_results.csv", {})
                .get("sha256", "")[:16],
            }
        )
    return rows


def load_cross_repo_benchmark_rows() -> list[dict[str, Any]]:
    """Cross-repo Eco-CI benchmark entries — real measured values only.

    See evidence/cross_repo_benchmark.yaml for provenance and the ground rule
    that "measured" rows must come from an actual checked GitHub Actions run,
    never an invented number.
    """
    if not CROSS_REPO_BENCHMARK_YAML.exists():
        return []
    doc = yaml.safe_load(CROSS_REPO_BENCHMARK_YAML.read_text(encoding="utf-8"))
    rows = []
    for entry in doc.get("entries", []):
        rows.append(
            {
                "Repo": entry.get("repo"),
                "Status": entry.get("status"),
                "SCI gCO2eq/Lauf": entry.get("sci_gco2eq_per_run"),
                "Energie (Joule)": entry.get("total_energy_joules"),
                "Ø CPU %": entry.get("avg_cpu_utilization_pct"),
                "Notiz": entry.get("notes"),
            }
        )
    return rows


def build_gate_contribution_rows(gate: AggregatedGateStatus) -> list[dict[str, Any]]:
    """Per-KPI breakdown behind an aggregated gate status, for the recommendation view."""
    return [
        {
            "KPI": f"{c.kpi_id} {c.kpi_name}",
            "Wert": round(c.value, 4),
            "Einheit": c.unit,
            "Zone": f"{ZONE_EMOJI.get(c.zone, '⚪')} {c.zone}",
        }
        for c in gate.contributions
    ]


def build_lever_ranking_rows(
    workload: WorkloadProfile,
    ef: EmissionFactorProfile,
    config_id: str,
    target: str = "co2",
) -> list[dict[str, Any]]:
    """Ranked control-variable impact rows for the "stärkster Hebel" view.

    target="co2" ranks by achievable gCO2e/request reduction, "cost" by achievable
    EUR/request (cost-per-useful-outcome) reduction — two separate rankings rather
    than one combined score, see generators/decision_support.py for why.
    """
    levers = (
        rank_co2_levers(workload, ef, config_id)
        if target == "co2"
        else rank_cost_levers(workload, ef, config_id)
    )
    unit = "gCO2e/Request" if target == "co2" else "EUR/Request"
    return [
        {
            "Stellhebel": lever.axis_label,
            "Von": lever.worse_value,
            "Nach": lever.better_value,
            f"Ergebnis bei 'Von' ({unit})": round(lever.worse_output, 6),
            f"Ergebnis bei 'Nach' ({unit})": round(lever.better_output, 6),
            f"Erreichbare Verbesserung ({unit})": round(lever.delta, 6),
        }
        for lever in levers
    ]


def build_demo_scenario_options() -> dict[str, DemoScenario]:
    """Named scenarios keyed by a dropdown-friendly label, for the sidebar selector."""
    return {f"{s.id} — {s.name}": s for s in list_demo_scenarios()}


BOAVIZTA_REFERENCES = [
    {
        "GPU-Modell": "NVIDIA L4",
        "VRAM GB": 24,
        "Embodied kgCO2eq": 113.6,
        "Verwendet für": "Tier 2 (24 GB)",
    },
    {
        "GPU-Modell": "NVIDIA RTX A4500",
        "VRAM GB": 20,
        "Embodied kgCO2eq": 141.4,
        "Verwendet für": "Tier 1 (16 GB, nächstliegende Referenz)",
    },
    {
        "GPU-Modell": "NVIDIA A100 PCIe 40GB",
        "VRAM GB": 40,
        "Embodied kgCO2eq": 275.7,
        "Verwendet für": "Basis für Tier 3/5 (interpoliert)",
    },
    {
        "GPU-Modell": "NVIDIA H100 SXM 80GB",
        "VRAM GB": 80,
        "Embodied kgCO2eq": 575.2,
        "Verwendet für": "Tier 4 (96 GB, nächstliegende Referenz)",
    },
]
