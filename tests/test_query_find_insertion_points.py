from pathlib import Path

from src.query_find_insertion_points import (
    query_find_insertion_points,
    query_find_insertion_points_for_file,
)


def test_query_find_insertion_points_empty_or_no_symbol_file(tmp_path: Path) -> None:
    (tmp_path / "empty.py").write_text("", encoding="utf-8")

    result = query_find_insertion_points_for_file(tmp_path, Path("empty.py"))

    assert result == {
        "found": True,
        "file_path": "empty.py",
        "candidates": [
            {
                "candidate_type": "file",
                "start_line": None,
                "end_line": None,
                "anchor_before_symbol_id": None,
                "anchor_after_symbol_id": None,
                "container_symbol_id": None,
                "precision": "file",
                "evidence_basis": "known_repo_file",
            }
        ],
    }


def test_query_find_insertion_points_single_top_level_symbol(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_find_insertion_points_for_file(tmp_path, Path("sample.py"))

    assert result == {
        "found": True,
        "file_path": "sample.py",
        "candidates": [
            {
                "candidate_type": "before_first_top_level_symbol",
                "start_line": 1,
                "end_line": 1,
                "anchor_before_symbol_id": None,
                "anchor_after_symbol_id": "sample.py:foo:1",
                "container_symbol_id": None,
                "precision": "line",
                "evidence_basis": "top_level_symbol_order",
            },
            {
                "candidate_type": "after_last_top_level_symbol",
                "start_line": 3,
                "end_line": 3,
                "anchor_before_symbol_id": "sample.py:foo:1",
                "anchor_after_symbol_id": None,
                "container_symbol_id": None,
                "precision": "line",
                "evidence_basis": "top_level_symbol_span",
            },
        ],
    }


def test_query_find_insertion_points_multiple_top_level_symbols(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text(
        "class Beta:\n"
        "    pass\n\n"
        "def alpha():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_find_insertion_points_for_file(tmp_path, Path("sample.py"))

    assert result == {
        "found": True,
        "file_path": "sample.py",
        "candidates": [
            {
                "candidate_type": "before_first_top_level_symbol",
                "start_line": 1,
                "end_line": 1,
                "anchor_before_symbol_id": None,
                "anchor_after_symbol_id": "sample.py:Beta:1",
                "container_symbol_id": None,
                "precision": "line",
                "evidence_basis": "top_level_symbol_order",
            },
            {
                "candidate_type": "between_top_level_symbols",
                "start_line": 2,
                "end_line": 4,
                "anchor_before_symbol_id": "sample.py:Beta:1",
                "anchor_after_symbol_id": "sample.py:alpha:4",
                "container_symbol_id": None,
                "precision": "region",
                "evidence_basis": "top_level_symbol_order",
            },
            {
                "candidate_type": "after_last_top_level_symbol",
                "start_line": 6,
                "end_line": 6,
                "anchor_before_symbol_id": "sample.py:alpha:4",
                "anchor_after_symbol_id": None,
                "container_symbol_id": None,
                "precision": "line",
                "evidence_basis": "top_level_symbol_span",
            },
        ],
    }


def test_query_find_insertion_points_symbol_container_candidate_when_supported(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_find_insertion_points(tmp_path, symbol_id="sample.py:foo:1")

    assert result == {
        "found": True,
        "file_path": "sample.py",
        "symbol_id": "sample.py:foo:1",
        "candidates": [
            {
                "candidate_type": "inside_container_symbol",
                "start_line": 1,
                "end_line": 2,
                "anchor_before_symbol_id": None,
                "anchor_after_symbol_id": None,
                "container_symbol_id": "sample.py:foo:1",
                "precision": "region",
                "evidence_basis": "symbol_span",
            }
        ],
    }


def test_query_find_insertion_points_ordering_is_deterministic(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text(
        "class Beta:\n"
        "    pass\n\n"
        "def alpha():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_find_insertion_points_for_file(tmp_path, Path("sample.py"))

    assert [candidate["candidate_type"] for candidate in result["candidates"]] == [
        "before_first_top_level_symbol",
        "between_top_level_symbols",
        "after_last_top_level_symbol",
    ]


def test_query_find_insertion_points_missing_file_stays_empty(tmp_path: Path) -> None:
    result = query_find_insertion_points_for_file(tmp_path, Path("missing.py"))

    assert result == {
        "found": False,
        "file_path": "missing.py",
        "candidates": [],
    }
