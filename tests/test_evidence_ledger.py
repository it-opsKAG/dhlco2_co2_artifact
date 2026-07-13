from datetime import datetime, timezone
from pathlib import Path

from evidence_ledger import _sha256_file, build_run_id


def test_build_run_id_matches_dissertation_schema():
    now = datetime(2026, 7, 14, 9, 30, 0, tzinfo=timezone.utc)
    run_id = build_run_id(claim_id="SIM", variant="fullsweep", now=now)

    assert run_id == "RUN-20260714T093000Z-SIM-fullsweep"


def test_sha256_file_is_stable_for_same_content(tmp_path: Path):
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.txt"
    file_a.write_text("identical content", encoding="utf-8")
    file_b.write_text("identical content", encoding="utf-8")

    assert _sha256_file(file_a) == _sha256_file(file_b)


def test_sha256_file_changes_when_content_changes(tmp_path: Path):
    file_path = tmp_path / "a.txt"
    file_path.write_text("version 1", encoding="utf-8")
    hash_v1 = _sha256_file(file_path)

    file_path.write_text("version 2", encoding="utf-8")
    hash_v2 = _sha256_file(file_path)

    assert hash_v1 != hash_v2
