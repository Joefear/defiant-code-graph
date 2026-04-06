from pathlib import Path

from src.repo_snapshot import build_repo_snapshot


def test_build_repo_snapshot(tmp_path: Path) -> None:
    first_root = tmp_path / "first"
    second_root = tmp_path / "second"
    third_root = tmp_path / "third"

    first_root.mkdir()
    second_root.mkdir()
    third_root.mkdir()

    (first_root / "b.py").write_text("print('b')\n", encoding="utf-8")
    (first_root / "a.py").write_text("print('a')\n", encoding="utf-8")

    (second_root / "a.py").write_text("print('a')\n", encoding="utf-8")
    (second_root / "b.py").write_text("print('b')\n", encoding="utf-8")

    (third_root / "a.py").write_text("print('a')\n", encoding="utf-8")

    first_snapshot = build_repo_snapshot(first_root)
    second_snapshot = build_repo_snapshot(second_root)
    third_snapshot = build_repo_snapshot(third_root)

    assert first_snapshot["snapshot_id"] == build_repo_snapshot(first_root)["snapshot_id"]
    assert first_snapshot["snapshot_id"] == second_snapshot["snapshot_id"]
    assert first_snapshot["snapshot_id"] != third_snapshot["snapshot_id"]
    assert first_snapshot["file_count"] == 2
    assert second_snapshot["file_count"] == 2
    assert third_snapshot["file_count"] == 1
