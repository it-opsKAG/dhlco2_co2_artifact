from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import yaml


def _load_yaml(path: Path) -> Dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping at top-level: {path}")
    return payload


def _sort_by_id(items: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda record: str(record.get("id", "")))


def _require_unique_ids(items: Sequence[Dict[str, Any]], label: str) -> None:
    ids = [str(item.get("id", "")).strip() for item in items]
    if any(not item_id for item_id in ids):
        raise ValueError(f"{label} contains empty ids")
    if len(ids) != len(set(ids)):
        raise ValueError(f"{label} contains duplicate ids")


def _validate_kpis_schema(kpis_doc: Dict[str, Any], schema_path: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    try:
        import jsonschema
    except ModuleNotFoundError as exc:  # pragma: no cover
        raise RuntimeError("jsonschema package is required for validation") from exc

    jsonschema.validate(instance=kpis_doc, schema=schema)


def _collect_tbd(value: Any, path: str, out: List[Tuple[str, str]]) -> None:
    if isinstance(value, dict):
        for key in sorted(value.keys()):
            child_path = f"{path}.{key}" if path else str(key)
            _collect_tbd(value[key], child_path, out)
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            child_path = f"{path}[{index}]"
            _collect_tbd(item, child_path, out)
        return
    if isinstance(value, str) and "TBD" in value:
        out.append((path, value))


def _ensure_export_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_text(path: Path, content: str) -> None:
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    path.write_text(normalized.rstrip() + "\n", encoding="utf-8")


def _csv_join(items: Iterable[str]) -> str:
    values = [str(item).strip() for item in items if str(item).strip()]
    return "; ".join(values)


def _md_escape(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ").strip()


def _render_kpi_catalog_md(kpis: Sequence[Dict[str, Any]]) -> str:
    lines = [
        "# KPI Catalog",
        "",
        "| ID | Phase | Name | Unit | Functional Unit | Lifecycle Steps | Emission Type | Data Sources | ISO Refs | Status | Source Refs |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for kpi in kpis:
        row = [
            _md_escape(kpi["id"]),
            _md_escape(kpi["phase"]),
            _md_escape(kpi["name"]),
            _md_escape(kpi["unit"]),
            _md_escape(kpi["functional_unit"]),
            _md_escape(_csv_join(kpi["lifecycle_steps"])),
            _md_escape(kpi["emission_type"]),
            _md_escape(_csv_join(kpi["data_sources"])),
            _md_escape(_csv_join(kpi["iso_refs"])),
            _md_escape(kpi["status"]),
            _md_escape(_csv_join(kpi["source_refs"])),
        ]
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def _write_kpi_catalog_csv(path: Path, kpis: Sequence[Dict[str, Any]]) -> None:
    headers = [
        "id",
        "phase",
        "name",
        "description",
        "formula",
        "unit",
        "functional_unit",
        "lifecycle_steps",
        "emission_type",
        "data_sources",
        "iso_refs",
        "status",
        "source_refs",
        "unknowns",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for kpi in kpis:
            writer.writerow(
                {
                    "id": kpi["id"],
                    "phase": kpi["phase"],
                    "name": kpi["name"],
                    "description": kpi["description"],
                    "formula": kpi["formula"],
                    "unit": kpi["unit"],
                    "functional_unit": kpi["functional_unit"],
                    "lifecycle_steps": _csv_join(kpi["lifecycle_steps"]),
                    "emission_type": kpi["emission_type"],
                    "data_sources": _csv_join(kpi["data_sources"]),
                    "iso_refs": _csv_join(kpi["iso_refs"]),
                    "status": kpi["status"],
                    "source_refs": _csv_join(kpi["source_refs"]),
                    "unknowns": _csv_join(kpi["unknowns"]),
                }
            )


def _render_lifecycle_md(
    steps: Sequence[Dict[str, Any]], mappings: Sequence[Dict[str, Any]]
) -> str:
    lines = [
        "# Lifecycle Mapping",
        "",
        "## Lifecycle Steps",
        "",
        "| ID | Step |",
        "| --- | --- |",
    ]
    for step in steps:
        lines.append(f"| {_md_escape(step['id'])} | {_md_escape(step['name'])} |")
    lines.extend(
        [
            "",
            "## KPI to Lifecycle Mapping",
            "",
            "| ID | KPI ID | Primary Step | Secondary Steps | Direct/Indirect | Source Refs |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for mapping in mappings:
        lines.append(
            "| {id} | {kpi_id} | {primary_step} | {secondary_steps} | {direct_or_indirect} | {source_refs} |".format(
                id=_md_escape(mapping["id"]),
                kpi_id=_md_escape(mapping["kpi_id"]),
                primary_step=_md_escape(mapping["primary_step"]),
                secondary_steps=_md_escape(_csv_join(mapping["secondary_steps"])),
                direct_or_indirect=_md_escape(mapping["direct_or_indirect"]),
                source_refs=_md_escape(_csv_join(mapping["source_refs"])),
            )
        )
    return "\n".join(lines)


def _render_gap_md(
    gaps: Sequence[Dict[str, Any]],
    proxies: Sequence[Dict[str, Any]],
    tbd_hits: Sequence[Tuple[str, str]],
) -> str:
    lines = [
        "# Gap Report",
        "",
        "## Declared Gaps",
        "",
        "| ID | Title | Impact | Required Input | Status | Source Refs |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for gap in gaps:
        lines.append(
            "| {id} | {title} | {impact} | {required_input} | {status} | {source_refs} |".format(
                id=_md_escape(gap["id"]),
                title=_md_escape(gap["title"]),
                impact=_md_escape(gap["impact"]),
                required_input=_md_escape(gap["required_input"]),
                status=_md_escape(gap["status"]),
                source_refs=_md_escape(_csv_join(gap["source_refs"])),
            )
        )

    lines.extend(
        [
            "",
            "## Proxies",
            "",
            "| ID | Gap ID | Proxy | Quality | Source Refs |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for proxy in proxies:
        lines.append(
            "| {id} | {gap_id} | {proxy} | {quality} | {source_refs} |".format(
                id=_md_escape(proxy["id"]),
                gap_id=_md_escape(proxy["gap_id"]),
                proxy=_md_escape(proxy["proxy"]),
                quality=_md_escape(proxy["quality"]),
                source_refs=_md_escape(_csv_join(proxy["source_refs"])),
            )
        )

    lines.extend(["", "## Derived TBD Entries", ""])
    if not tbd_hits:
        lines.append("- None")
    else:
        for path, value in tbd_hits:
            lines.append(f"- `{path}`: {_md_escape(value)}")
    return "\n".join(lines)


def build_exports(data_dir: Path, schema_path: Path, export_dir: Path) -> None:
    kpis_doc = _load_yaml(data_dir / "kpis.yaml")
    lifecycle_doc = _load_yaml(data_dir / "lifecycle_mapping.yaml")
    assumptions_doc = _load_yaml(data_dir / "assumptions_proxies.yaml")

    _validate_kpis_schema(kpis_doc, schema_path)

    kpis = _sort_by_id(list(kpis_doc.get("kpis", [])))
    steps = _sort_by_id(list(lifecycle_doc.get("lifecycle_steps", [])))
    mappings = _sort_by_id(list(lifecycle_doc.get("kpi_mappings", [])))
    gaps = _sort_by_id(list(assumptions_doc.get("gaps", [])))
    proxies = _sort_by_id(list(assumptions_doc.get("proxies", [])))

    _require_unique_ids(kpis, "kpis")
    _require_unique_ids(steps, "lifecycle_steps")
    _require_unique_ids(mappings, "kpi_mappings")
    _require_unique_ids(gaps, "gaps")
    _require_unique_ids(proxies, "proxies")

    tbd_hits: List[Tuple[str, str]] = []
    _collect_tbd(kpis_doc, "kpis_doc", tbd_hits)
    _collect_tbd(lifecycle_doc, "lifecycle_doc", tbd_hits)
    _collect_tbd(assumptions_doc, "assumptions_doc", tbd_hits)
    tbd_hits_sorted = sorted(set(tbd_hits), key=lambda item: (item[0], item[1]))

    _ensure_export_dir(export_dir)
    _write_text(export_dir / "KPI_Catalog.md", _render_kpi_catalog_md(kpis))
    _write_kpi_catalog_csv(export_dir / "KPI_Catalog.csv", kpis)
    _write_text(
        export_dir / "Lifecycle_Mapping.md",
        _render_lifecycle_md(steps=steps, mappings=mappings),
    )
    _write_text(
        export_dir / "Gap_Report.md",
        _render_gap_md(gaps=gaps, proxies=proxies, tbd_hits=tbd_hits_sorted),
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default=str(root / "data"))
    parser.add_argument("--schema-path", default=str(root / "schema" / "kpis.schema.json"))
    parser.add_argument("--export-dir", default=str(root / "exports"))
    args = parser.parse_args()

    build_exports(
        data_dir=Path(args.data_dir),
        schema_path=Path(args.schema_path),
        export_dir=Path(args.export_dir),
    )


if __name__ == "__main__":
    main()
