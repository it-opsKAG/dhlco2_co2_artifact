"""Named, illustrative DHL-style demo scenarios for the decision-support dashboard.

Loads data/demo_scenarios.yaml and converts each entry into the same WorkloadProfile /
EmissionFactorProfile objects the rest of the model (hardware_model.py, rdc_pareto.py,
decision_support.py) already consumes — so a named scenario is not a parallel data
model, just a labeled preset over the existing one.

See docs/demo_scenario_matrix.md for the coverage rationale (which function-type x
volume-class combinations are covered, which are deliberately left open, and why).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml

from hardware_model import EmissionFactorProfile, WorkloadProfile

_ROOT = Path(__file__).resolve().parent.parent
_SCENARIOS_YAML = _ROOT / "data" / "demo_scenarios.yaml"
_MATRIX_DOC = _ROOT / "docs" / "demo_scenario_matrix.md"

FUNCTION_AXIS_LABELS = {
    "K1": "Kundeninteraktion Echtzeit",
    "K2": "Bilderkennung/Sortierung Echtzeit",
    "K3": "Batch-Analytics/Prognose",
    "K4": "Vorausschauende Wartung/Anomalieerkennung",
}
VOLUME_AXIS_LABELS = {
    "V1": "niedrig (~1k/Monat)",
    "V2": "mittel (~10k/Monat)",
    "V3": "hoch (~100k/Monat)",
    "V4": "sehr hoch (~1M+/Monat)",
}


@dataclass(frozen=True)
class DemoScenario:
    id: str
    name: str
    description: str
    notes: str
    function_axis: Optional[str]
    volume_axis: Optional[str]
    is_edge_case: bool
    min_vram_gb: float
    requests_per_month: int
    avg_latency_s: float
    quality_score: float
    business_value_score: float
    grid_ef_gco2e_per_kwh: float
    pv_share: float

    @property
    def function_label(self) -> str:
        if self.function_axis is None:
            return "—"
        return f"{self.function_axis} {FUNCTION_AXIS_LABELS.get(self.function_axis, '')}"

    @property
    def volume_label(self) -> str:
        if self.volume_axis is None:
            return "—"
        return f"{self.volume_axis} {VOLUME_AXIS_LABELS.get(self.volume_axis, '')}"

    def to_workload(self) -> WorkloadProfile:
        return WorkloadProfile(
            id=self.id,
            model_size_b=70,
            quantization="Q4_K_M",
            min_vram_gb=self.min_vram_gb,
            requests_per_month=self.requests_per_month,
            quality_score=self.quality_score,
            business_value_score=self.business_value_score,
            avg_latency_s=self.avg_latency_s,
        )

    def to_emission_factor(self) -> EmissionFactorProfile:
        return EmissionFactorProfile(
            grid_ef_gco2e_per_kwh=self.grid_ef_gco2e_per_kwh,
            pv_share=self.pv_share,
        )


def _parse_scenario(entry: dict) -> DemoScenario:
    workload = entry["workload"]
    ef = entry["emission_factor"]
    return DemoScenario(
        id=entry["id"],
        name=entry["name"],
        description=entry["description"].strip(),
        notes=entry.get("notes", "").strip(),
        function_axis=entry.get("function_axis"),
        volume_axis=entry.get("volume_axis"),
        is_edge_case=bool(entry.get("is_edge_case", False)),
        min_vram_gb=workload["min_vram_gb"],
        requests_per_month=workload["requests_per_month"],
        avg_latency_s=workload["avg_latency_s"],
        quality_score=workload["quality_score"],
        business_value_score=workload["business_value_score"],
        grid_ef_gco2e_per_kwh=ef["grid_ef_gco2e_per_kwh"],
        pv_share=ef["pv_share"],
    )


def list_demo_scenarios() -> list[DemoScenario]:
    doc = yaml.safe_load(_SCENARIOS_YAML.read_text(encoding="utf-8"))
    return [_parse_scenario(entry) for entry in doc.get("demo_scenarios", [])]


def get_demo_scenario(scenario_id: str) -> DemoScenario:
    for scenario in list_demo_scenarios():
        if scenario.id == scenario_id:
            return scenario
    raise KeyError(f"Unknown demo scenario id: {scenario_id!r}")


def coverage_summary() -> dict[str, object]:
    """Cross-check docs/demo_scenario_matrix.md's referenced IDs against the YAML.

    Lightweight analog to economic_intelligence_engine's coverage_report.py: guards
    against doc/data drift (a scenario renamed or removed in the YAML but still
    referenced in the matrix doc, or vice versa) rather than re-deriving the matrix
    itself. See tests/test_demo_scenarios.py for the CI-gate assertions.
    """
    yaml_ids = {s.id for s in list_demo_scenarios()}
    doc_text = _MATRIX_DOC.read_text(encoding="utf-8")
    doc_ids = set(re.findall(r"DEMO-\d\d", doc_text))
    return {
        "yaml_ids": yaml_ids,
        "doc_ids": doc_ids,
        "in_yaml_not_in_doc": yaml_ids - doc_ids,
        "in_doc_not_in_yaml": doc_ids - yaml_ids,
    }


if __name__ == "__main__":
    scenarios = list_demo_scenarios()
    print(f"{len(scenarios)} demo scenarios loaded from {_SCENARIOS_YAML.name}:")
    for s in scenarios:
        edge = " [Edge-Case]" if s.is_edge_case else ""
        print(f"  {s.id}{edge}: {s.name} ({s.function_label} x {s.volume_label})")

    summary = coverage_summary()
    if summary["in_yaml_not_in_doc"] or summary["in_doc_not_in_yaml"]:
        print("\nCoverage drift detected:")
        print(f"  in YAML but not in matrix doc: {summary['in_yaml_not_in_doc']}")
        print(f"  in matrix doc but not in YAML: {summary['in_doc_not_in_yaml']}")
    else:
        print("\nCoverage matrix doc and YAML are in sync.")
