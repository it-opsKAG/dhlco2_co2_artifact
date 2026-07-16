"""Green Gate loading and zone classification — pure logic, no Streamlit dependency.

Moved out of dashboard/data_helpers.py so generators/decision_support.py can reuse
the same zone-classification rule without creating a generators -> dashboard
dependency (dashboard depends on generators, not the reverse). dashboard/data_helpers.py
re-exports these names so existing imports there keep working unchanged.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_ROOT = Path(__file__).resolve().parent.parent
_GREEN_GATES_YAML = _ROOT / "data" / "green_gates.yaml"


def load_green_gates() -> dict[str, dict[str, Any]]:
    doc = yaml.safe_load(_GREEN_GATES_YAML.read_text(encoding="utf-8"))
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
