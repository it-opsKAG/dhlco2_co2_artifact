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


def load_kpi_catalog() -> list[dict[str, Any]]:
    doc = yaml.safe_load((DATA_DIR / "kpis.yaml").read_text(encoding="utf-8"))
    return list(doc.get("kpis", []))


def load_green_gates() -> dict[str, dict[str, Any]]:
    doc = yaml.safe_load((DATA_DIR / "green_gates.yaml").read_text(encoding="utf-8"))
    return {str(gate["kpi_id"]): gate for gate in doc.get("green_gates", [])}


def has_defined_gate(gate: dict[str, Any] | None) -> bool:
    """True if a green_gates.yaml entry has an actual numeric threshold defined.

    Used for presence-checks (e.g. the KPI catalog tab) without needing a real
    value to classify — avoids calling gate_zone() with a meaningless placeholder.
    """
    if not gate:
        return False
    green = gate.get("thresholds", {}).get("green", {})
    return green.get("max") is not None or green.get("min") is not None


def gate_zone(value: float, gate: dict[str, Any] | None) -> str:
    """Classify a numeric value into green/amber/red per a green_gates.yaml entry.

    Returns "tbd" if the gate has no numeric thresholds yet (threshold_basis: tbd),
    no gate entry exists at all (e.g. SCI-001/SCI-002 currently have no defined gate —
    verified 2026-07-15: these two aggregate/boundary-dependent KPIs have no entry in
    data/green_gates.yaml, likely because a universal numeric threshold doesn't make
    sense without a fixed functional-unit scale; not treated as a bug here), or the
    gate uses non-numeric ordinal thresholds (e.g. GOV-002's "M0".."M3" maturity
    levels) that this function does not attempt to classify.
    """
    if not has_defined_gate(gate):
        return "tbd"
    thresholds = gate["thresholds"]
    green = thresholds["green"]

    # Non-numeric (ordinal) thresholds, e.g. GOV-002's "M0".."M3" — not handled here.
    if not isinstance(green.get("max", green.get("min")), (int, float)):
        return "tbd"

    # "higher is better" gates use min-based green/red (e.g. RUN-004 energy proportionality)
    if "min" in green:
        if value >= green["min"]:
            return "green"
        if "min" in thresholds.get("amber", {}) and value >= thresholds["amber"]["min"]:
            return "amber"
        return "red"

    # "lower is better" gates use max-based green/red (most KPIs)
    if value <= green.get("max", float("inf")):
        return "green"
    amber_max = thresholds.get("amber", {}).get("max")
    if amber_max is not None and value <= amber_max:
        return "amber"
    return "red"


ZONE_EMOJI = {"green": "\U0001F7E2", "amber": "\U0001F7E1", "red": "\U0001F534", "tbd": "⚪"}


def build_scenario_rows(
    workload: WorkloadProfile, ef: EmissionFactorProfile
) -> list[dict[str, Any]]:
    """Hardware comparison rows for the current sidebar scenario (feasible configs only)."""
    ranked = rdc_rank(workload, ef)
    rows = []
    for r in ranked:
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
