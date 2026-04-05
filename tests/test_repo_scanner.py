from pathlib import Path

from src.repo_scanner import scan_repository


def test_scan_repository_includes_files_excludes_directories_and_returns_sorted_paths(
    tmp_path: Path,
) -> None:
    included_file = tmp_path / "alpha.txt"
    included_file.write_text("included", encoding="utf-8")

    excluded_file = tmp_path / ".git" / "ignored.txt"
    excluded_file.parent.mkdir()
    excluded_file.write_text("excluded", encoding="utf-8")

    result = scan_repository(tmp_path)

    assert result == [included_file]
    assert len(result) == 1
    assert result == sorted(result)
