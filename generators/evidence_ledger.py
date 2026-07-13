"""Evidence Ledger — turns simulation runs into individually citable RUN-artifacts.

Problem this solves: the presentation deck asserts "192 scenarios, 816 result rows" as a
bare claim in prose. This module makes that claim independently verifiable: it re-runs the
deterministic simulation, hashes the outputs, stamps a RUN-ID and the exact git commit the
run was produced from, and appends an append-only ledger entry. Anyone can later re-run
`generators/simulation_runner.py` at the same commit and confirm the hashes match.

RUN-ID schema (same convention as the dissertation evidence ledger, see
knowledge_vault 30_Forschung/Dissertation validation-matrix pattern):
  RUN-{YYYYMMDD}T{HHMMSS}Z-{CLAIM_ID}-{VARIANT}

Usage:
  PYTHONUTF8=1 python generators/evidence_ledger.py
  PYTHONUTF8=1 python generators/evidence_ledger.py --claim-id SIM --variant fullsweep
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))

from simulation_runner import SCENARIO_AXES, _build_scenarios, run_simulation

REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "evidence"
LEDGER_JSONL = EVIDENCE_DIR / "simulation_runs.jsonl"
LEDGER_MD = EVIDENCE_DIR / "SIMULATION_EVIDENCE_LEDGER.md"


def _git_commit() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def _git_dirty() -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
        return bool(result.stdout.strip())
    except Exception:
        return True  # unknown state — treat conservatively as dirty


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def build_run_id(*, claim_id: str, variant: str, now: datetime) -> str:
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    return f"RUN-{stamp}-{claim_id}-{variant}"


def record_simulation_run(
    *,
    claim_id: str = "SIM",
    variant: str = "fullsweep",
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run the simulation sweep, hash the outputs, and append a ledger entry."""
    now = datetime.now(timezone.utc)
    output_dir = output_dir or (REPO_ROOT / "exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    scenarios = _build_scenarios()
    rows = run_simulation(output_dir=output_dir)

    csv_path = output_dir / "simulation_results.csv"
    summary_path = output_dir / "simulation_summary.md"

    run_id = build_run_id(claim_id=claim_id, variant=variant, now=now)
    manifest: dict[str, Any] = {
        "run_id": run_id,
        "created_at": now.isoformat(timespec="seconds"),
        "claim_id": claim_id,
        "variant": variant,
        "claim_text": (
            "Simulation sweep over hardware tiers and control-variable scenarios "
            "produces a deterministic, reproducible set of CO2/EUR/EfficiencyScore "
            "results (backs the 'X Szenarien, Y Zeilen' figure shown in the status deck)."
        ),
        "git_commit": _git_commit(),
        "git_dirty": _git_dirty(),
        "scenario_axes": SCENARIO_AXES,
        "scenario_count": len(scenarios),
        "result_row_count": len(rows),
        "unique_hardware_configs": len({row["hw_id"] for row in rows}),
        "outputs": {
            "simulation_results.csv": {
                "sha256": _sha256_file(csv_path),
                "row_count": len(rows),
            },
            "simulation_summary.md": {
                "sha256": _sha256_file(summary_path),
            },
        },
        "reproduce_with": (
            "PYTHONUTF8=1 python generators/evidence_ledger.py "
            f"--claim-id {claim_id} --variant {variant}"
        ),
    }

    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    with LEDGER_JSONL.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(manifest, ensure_ascii=False) + "\n")

    _rewrite_ledger_md()
    return manifest


def _load_ledger_entries() -> list[dict[str, Any]]:
    if not LEDGER_JSONL.exists():
        return []
    entries = []
    for line in LEDGER_JSONL.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entries.append(json.loads(line))
    return entries


def _rewrite_ledger_md() -> None:
    entries = _load_ledger_entries()
    lines = [
        "# Simulation Evidence Ledger",
        "",
        "Append-only record of simulation runs. Each row is independently reproducible: "
        "check out the referenced git commit, re-run `generators/evidence_ledger.py`, and "
        "confirm the output hashes match. This ledger backs the scenario/row-count figures "
        "quoted in customer-facing materials with a concrete, auditable artifact instead of "
        "a bare number.",
        "",
        "| Run ID | Created (UTC) | Git Commit | Dirty | Scenarios | Rows | HW Configs | CSV SHA-256 (short) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for entry in entries:
        commit = str(entry.get("git_commit", "unknown"))[:12]
        csv_hash = entry.get("outputs", {}).get("simulation_results.csv", {}).get("sha256", "")[:12]
        lines.append(
            "| {run_id} | {created_at} | `{commit}` | {dirty} | {scenarios} | {rows} | {hw} | `{csv_hash}` |".format(
                run_id=entry.get("run_id", ""),
                created_at=entry.get("created_at", ""),
                commit=commit,
                dirty=entry.get("git_dirty", "unknown"),
                scenarios=entry.get("scenario_count", ""),
                rows=entry.get("result_row_count", ""),
                hw=entry.get("unique_hardware_configs", ""),
                csv_hash=csv_hash,
            )
        )
    lines += [
        "",
        "## Full manifests",
        "",
        "See `evidence/simulation_runs.jsonl` (one JSON manifest per line) for the complete "
        "record per run, including the exact scenario-axis parameters and full SHA-256 hashes.",
    ]
    LEDGER_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a simulation run in the evidence ledger")
    parser.add_argument("--claim-id", default="SIM")
    parser.add_argument("--variant", default="fullsweep")
    args = parser.parse_args()

    manifest = record_simulation_run(claim_id=args.claim_id, variant=args.variant)
    print(f"Recorded {manifest['run_id']}")
    print(f"  scenarios={manifest['scenario_count']} rows={manifest['result_row_count']}")
    print(f"  git_commit={manifest['git_commit']} dirty={manifest['git_dirty']}")
    print(f"  ledger: {LEDGER_JSONL.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
