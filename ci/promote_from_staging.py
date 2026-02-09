from __future__ import annotations

import argparse
import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import yaml


@dataclass(frozen=True)
class Rule:
    rule_id: str
    source_glob: str
    destination: str


@dataclass(frozen=True)
class Candidate:
    source_rel: str
    source_abs: Path
    run_id: str
    destination_rel: Optional[str]
    source_sha256: str
    approved: bool
    approval_note: str
    promotion_status: str
    destination_sha256: Optional[str]


def _run_git(repo: Path, args: Sequence[str], check: bool = False) -> subprocess.CompletedProcess:
    cmd = ["git", "-C", str(repo), *args]
    return subprocess.run(cmd, capture_output=True, text=True, check=check)


def _is_git_repo(path: Path) -> bool:
    proc = _run_git(path, ["rev-parse", "--is-inside-work-tree"])
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def _git_head(repo: Path) -> str:
    proc = _run_git(repo, ["rev-parse", "HEAD"])
    if proc.returncode != 0:
        return "NO_COMMIT"
    return proc.stdout.strip()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_yaml_mapping(path: Path) -> Dict:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected mapping YAML at {path}")
    return payload


def _load_rules(path: Path) -> List[Rule]:
    payload = _load_yaml_mapping(path)
    raw_rules = payload.get("rules", [])
    if not isinstance(raw_rules, list):
        raise ValueError("Allowlist rules must be a list")
    rules: List[Rule] = []
    for raw_rule in raw_rules:
        if not isinstance(raw_rule, dict):
            raise ValueError("Every allowlist rule must be a mapping")
        rules.append(
            Rule(
                rule_id=str(raw_rule["id"]),
                source_glob=str(raw_rule["source_glob"]),
                destination=str(raw_rule["destination"]),
            )
        )
    rules.sort(key=lambda item: item.rule_id)
    return rules


def _load_registry(path: Path) -> Dict:
    if not path.exists():
        return {"version": 1, "promotions": []}
    payload = _load_yaml_mapping(path)
    payload.setdefault("version", 1)
    payload.setdefault("promotions", [])
    if not isinstance(payload["promotions"], list):
        raise ValueError("Registry field 'promotions' must be a list")
    return payload


def _latest_registry_hash_index(registry: Dict) -> Dict[str, str]:
    index: Dict[str, str] = {}
    for record in registry.get("promotions", []):
        files = record.get("files", [])
        if not isinstance(files, list):
            continue
        for file_record in files:
            if not isinstance(file_record, dict):
                continue
            source_rel = str(file_record.get("source_rel", "")).strip()
            source_sha = str(file_record.get("source_sha256", "")).strip()
            if source_rel and source_sha:
                index[source_rel] = source_sha
    return index


def _extract_run_id(source_rel: str) -> str:
    parts = PurePosixPath(source_rel).parts
    if len(parts) < 3:
        return "UNKNOWN_RUN"
    if parts[0] != "outputs" or parts[1] != "dhlco2_phase1":
        return "UNKNOWN_RUN"
    return parts[2]


def _resolve_destination(source_rel: str, rules: Sequence[Rule]) -> Optional[str]:
    run_id = _extract_run_id(source_rel)
    source_path = PurePosixPath(source_rel)
    for rule in rules:
        if source_path.match(rule.source_glob):
            basename = source_path.name
            return rule.destination.format(run_id=run_id, basename=basename)
    return None


def _iter_source_files(staging_repo: Path, source_run_dir: str) -> List[Tuple[str, Path]]:
    source_root = staging_repo / source_run_dir
    if not source_root.exists():
        raise FileNotFoundError(f"Source run dir not found: {source_root}")
    files: List[Tuple[str, Path]] = []
    for item in sorted(source_root.rglob("*")):
        if item.is_file():
            rel = item.relative_to(staging_repo).as_posix()
            files.append((rel, item))
    return files


def _is_file_clean_at_head(staging_repo: Path, source_rel: str) -> Tuple[bool, str]:
    tracked = _run_git(staging_repo, ["ls-files", "--error-unmatch", "--", source_rel])
    if tracked.returncode != 0:
        return (False, "not tracked in git")

    unstaged = _run_git(staging_repo, ["diff", "--quiet", "--", source_rel])
    if unstaged.returncode != 0:
        return (False, "has unstaged changes")

    staged = _run_git(staging_repo, ["diff", "--cached", "--quiet", "--", source_rel])
    if staged.returncode != 0:
        return (False, "has staged changes")

    return (True, "clean at HEAD")


def _destination_sha(root: Path, destination_rel: Optional[str]) -> Optional[str]:
    if not destination_rel:
        return None
    destination_abs = root / destination_rel
    if not destination_abs.exists():
        return None
    return _file_sha256(destination_abs)


def _promotion_status(
    source_sha: str,
    destination_rel: Optional[str],
    destination_sha: Optional[str],
    registry_index: Dict[str, str],
    source_rel: str,
) -> str:
    if not destination_rel:
        return "unmapped"
    registry_sha = registry_index.get(source_rel)
    if registry_sha == source_sha and destination_sha == source_sha:
        return "promoted"
    if destination_sha == source_sha:
        return "copied_unregistered"
    return "pending"


def _build_candidates(
    *,
    root: Path,
    staging_repo: Path,
    source_run_dir: str,
    rules: Sequence[Rule],
    approval_mode: str,
    registry_index: Dict[str, str],
) -> List[Candidate]:
    candidates: List[Candidate] = []
    for source_rel, source_abs in _iter_source_files(staging_repo, source_run_dir):
        run_id = _extract_run_id(source_rel)
        destination_rel = _resolve_destination(source_rel, rules)
        source_sha = _file_sha256(source_abs)
        if approval_mode == "committed_head":
            approved, approval_note = _is_file_clean_at_head(staging_repo, source_rel)
        else:
            approved, approval_note = (True, "worktree mode")
        destination_sha = _destination_sha(root, destination_rel)
        status = _promotion_status(
            source_sha=source_sha,
            destination_rel=destination_rel,
            destination_sha=destination_sha,
            registry_index=registry_index,
            source_rel=source_rel,
        )
        candidates.append(
            Candidate(
                source_rel=source_rel,
                source_abs=source_abs,
                run_id=run_id,
                destination_rel=destination_rel,
                source_sha256=source_sha,
                approved=approved,
                approval_note=approval_note,
                promotion_status=status,
                destination_sha256=destination_sha,
            )
        )
    candidates.sort(key=lambda item: item.source_rel)
    return candidates


def _copy_file(source_abs: Path, destination_abs: Path) -> None:
    destination_abs.parent.mkdir(parents=True, exist_ok=True)
    data = source_abs.read_bytes()
    destination_abs.write_bytes(data)


def _next_promotion_id(registry: Dict) -> str:
    promotions = registry.get("promotions", [])
    max_index = 0
    for record in promotions:
        raw_id = str(record.get("id", ""))
        if raw_id.startswith("PROMO-"):
            suffix = raw_id.split("-", 1)[1]
            if suffix.isdigit():
                max_index = max(max_index, int(suffix))
    return f"PROMO-{max_index + 1:04d}"


def _append_registry_record(
    *,
    registry: Dict,
    source_run_dir: str,
    staging_repo_rel: str,
    staging_head: str,
    approval_mode: str,
    promoted_files: Sequence[Candidate],
) -> None:
    files_payload = []
    for item in promoted_files:
        files_payload.append(
            {
                "source_rel": item.source_rel,
                "destination_rel": item.destination_rel,
                "source_sha256": item.source_sha256,
            }
        )
    files_payload.sort(key=lambda row: row["source_rel"])
    record = {
        "id": _next_promotion_id(registry),
        "source_run_dir": source_run_dir,
        "staging_repo": staging_repo_rel,
        "staging_head": staging_head,
        "approval_mode": approval_mode,
        "files": files_payload,
    }
    registry["promotions"].append(record)


def _write_registry(path: Path, registry: Dict) -> None:
    stable = {
        "version": int(registry.get("version", 1)),
        "promotions": registry.get("promotions", []),
    }
    payload = yaml.safe_dump(stable, sort_keys=False, allow_unicode=False)
    path.write_text(payload, encoding="utf-8")


def _print_report(candidates: Sequence[Candidate]) -> None:
    print("source_rel | approved | promotion_status | destination_rel")
    for item in candidates:
        destination_rel = item.destination_rel or "-"
        approved = "yes" if item.approved else "no"
        print(f"{item.source_rel} | {approved} | {item.promotion_status} | {destination_rel}")


def _select_for_apply(candidates: Sequence[Candidate]) -> List[Candidate]:
    selected = []
    for item in candidates:
        if not item.approved:
            continue
        if not item.destination_rel:
            continue
        if item.promotion_status == "promoted":
            continue
        selected.append(item)
    return selected


def _apply_promotions(root: Path, selected: Sequence[Candidate]) -> None:
    for item in selected:
        destination_abs = root / str(item.destination_rel)
        _copy_file(item.source_abs, destination_abs)


def _repo_relative_path(base: Path, target: Path) -> str:
    try:
        return target.resolve().relative_to(base.resolve()).as_posix()
    except ValueError:
        return str(target.resolve())


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    workspace_root = root.parents[1]

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--staging-repo",
        default=str(workspace_root / "staging"),
        help="Path to staging git repository.",
    )
    parser.add_argument(
        "--source-run-dir",
        default="outputs/dhlco2_phase1/phase1_initial",
        help="Run directory inside staging repo.",
    )
    parser.add_argument(
        "--allowlist",
        default=str(root / "ci" / "promotion_allowlist.yaml"),
        help="Allowlist mapping file.",
    )
    parser.add_argument(
        "--registry",
        default=str(root / "data" / "promotion_registry.yaml"),
        help="Promotion registry file.",
    )
    parser.add_argument(
        "--approval-mode",
        choices=["committed_head", "worktree"],
        default="committed_head",
        help="Approval gate for source files.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Copy approved pending files and update registry.",
    )
    args = parser.parse_args()

    staging_repo = Path(args.staging_repo).resolve()
    allowlist_path = Path(args.allowlist).resolve()
    registry_path = Path(args.registry).resolve()

    if not _is_git_repo(staging_repo):
        raise SystemExit(f"Not a git repo: {staging_repo}")
    if not allowlist_path.exists():
        raise SystemExit(f"Allowlist not found: {allowlist_path}")

    rules = _load_rules(allowlist_path)
    registry = _load_registry(registry_path)
    registry_index = _latest_registry_hash_index(registry)

    candidates = _build_candidates(
        root=root,
        staging_repo=staging_repo,
        source_run_dir=args.source_run_dir,
        rules=rules,
        approval_mode=args.approval_mode,
        registry_index=registry_index,
    )
    _print_report(candidates)

    selected = _select_for_apply(candidates)
    print(f"pending_promotions={len(selected)}")

    if not args.apply:
        return

    if not selected:
        print("apply: no changes")
        return

    _apply_promotions(root, selected)

    staging_head = _git_head(staging_repo)
    _append_registry_record(
        registry=registry,
        source_run_dir=args.source_run_dir,
        staging_repo_rel=_repo_relative_path(root, staging_repo),
        staging_head=staging_head,
        approval_mode=args.approval_mode,
        promoted_files=selected,
    )
    _write_registry(registry_path, registry)

    print(f"apply: promoted_files={len(selected)}")


if __name__ == "__main__":
    main()
