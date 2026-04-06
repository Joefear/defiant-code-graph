from pathlib import Path

from src.query_determine_edit_strategy import query_determine_edit_strategy


def test_query_determine_edit_strategy_clean_insert_new_case(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n\n"
        "def bar():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    result = query_determine_edit_strategy(
        tmp_path,
        file_path=Path("sample.py"),
        proposed_start_line=3,
        proposed_end_line=3,
    )

    assert result["found"] is True
    assert result["strategy"] == "insert_new"
    assert result["precision"] == "line"
    assert result["evidence_basis"] == ["top_level_symbol_order", "top_level_symbol_span"]


def test_query_determine_edit_strategy_rewrite_due_to_symbol_collision(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_determine_edit_strategy(
        tmp_path,
        file_path=Path("sample.py"),
        proposed_start_line=1,
        proposed_end_line=2,
    )

    assert result["found"] is True
    assert result["strategy"] == "rewrite"
    assert result["precision"] == "line"
    assert result["evidence_basis"] == ["symbol_span_overlap"]


def test_query_determine_edit_strategy_extend_when_symbol_context_supported(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_determine_edit_strategy(
        tmp_path,
        symbol_id="sample.py:foo:1",
        proposed_start_line=3,
        proposed_end_line=3,
    )

    assert result["found"] is True
    assert result["strategy"] == "extend"
    assert result["precision"] == "region"
    assert result["evidence_basis"] == ["symbol_span"]


def test_query_determine_edit_strategy_unknown_when_only_protected_file_fact_exists(
    tmp_path: Path,
) -> None:
    (tmp_path / "locked.py").write_text(
        "# @locked\n"
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_determine_edit_strategy(
        tmp_path,
        file_path=Path("locked.py"),
        proposed_start_line=4,
        proposed_end_line=4,
    )

    assert result["found"] is True
    assert result["strategy"] == "unknown"
    assert result["precision"] == "file"
    assert result["evidence_basis"] == ["file_ownership_facts"]


def test_query_determine_edit_strategy_missing_target(tmp_path: Path) -> None:
    result = query_determine_edit_strategy(
        tmp_path,
        file_path=Path("missing.py"),
        proposed_start_line=1,
        proposed_end_line=1,
    )

    assert result == {
        "found": False,
        "file_path": "missing.py",
        "symbol_id": None,
        "proposed_region": {"start_line": 1, "end_line": 1},
        "strategy": "unknown",
        "supporting_facts": {
            "insertion_candidates": [],
            "collision_result": {
                "found": False,
                "file_path": "missing.py",
                "symbol_id": None,
                "proposed_region": {"start_line": 1, "end_line": 1},
                "collision_detected": False,
                "symbol_collisions": [],
                "protected_collisions": [],
                "precision": None,
                "evidence_basis": [],
            },
        },
        "precision": None,
        "evidence_basis": [],
    }
