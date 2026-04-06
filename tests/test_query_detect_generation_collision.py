from pathlib import Path

from src.query_detect_generation_collision import query_detect_generation_collision


def test_query_detect_generation_collision_no_collision_in_open_region(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n\n"
        "def bar():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    result = query_detect_generation_collision(
        tmp_path,
        file_path=Path("sample.py"),
        proposed_start_line=3,
        proposed_end_line=3,
    )

    assert result == {
        "found": True,
        "file_path": "sample.py",
        "symbol_id": None,
        "proposed_region": {"start_line": 3, "end_line": 3},
        "collision_detected": False,
        "symbol_collisions": [],
        "protected_collisions": [],
        "precision": None,
        "evidence_basis": [],
    }


def test_query_detect_generation_collision_symbol_span_overlap(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n\n"
        "def bar():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    result = query_detect_generation_collision(
        tmp_path,
        file_path=Path("sample.py"),
        proposed_start_line=4,
        proposed_end_line=4,
    )

    assert result == {
        "found": True,
        "file_path": "sample.py",
        "symbol_id": None,
        "proposed_region": {"start_line": 4, "end_line": 4},
        "collision_detected": True,
        "symbol_collisions": [
            {
                "symbol_id": "sample.py:bar:4",
                "symbol_name": "bar",
                "symbol_kind": "function",
                "span": {"start_line": 4, "end_line": 5},
                "precision": "line",
                "evidence_basis": "symbol_span_overlap",
            }
        ],
        "protected_collisions": [],
        "precision": "line",
        "evidence_basis": ["symbol_span_overlap"],
    }


def test_query_detect_generation_collision_reports_protected_file_collision(
    tmp_path: Path,
) -> None:
    (tmp_path / "locked.py").write_text(
        "# @locked\n"
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_detect_generation_collision(
        tmp_path,
        file_path=Path("locked.py"),
        proposed_start_line=4,
        proposed_end_line=4,
    )

    assert result == {
        "found": True,
        "file_path": "locked.py",
        "symbol_id": None,
        "proposed_region": {"start_line": 4, "end_line": 4},
        "collision_detected": True,
        "symbol_collisions": [],
        "protected_collisions": [
            {
                "file_path": "locked.py",
                "protection_class": "locked",
                "evidence_basis": "file_ownership_facts",
                "precision": "file",
                "requested_region": {"start_line": 4, "end_line": 4},
            }
        ],
        "precision": "file",
        "evidence_basis": ["file_ownership_facts"],
    }


def test_query_detect_generation_collision_missing_file_stays_empty(
    tmp_path: Path,
) -> None:
    result = query_detect_generation_collision(
        tmp_path,
        file_path=Path("missing.py"),
        proposed_start_line=1,
        proposed_end_line=2,
    )

    assert result == {
        "found": False,
        "file_path": "missing.py",
        "symbol_id": None,
        "proposed_region": {"start_line": 1, "end_line": 2},
        "collision_detected": False,
        "symbol_collisions": [],
        "protected_collisions": [],
        "precision": None,
        "evidence_basis": [],
    }


def test_query_detect_generation_collision_ordering_is_deterministic(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "class Beta:\n"
        "    pass\n\n"
        "def alpha():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_detect_generation_collision(
        tmp_path,
        file_path=Path("sample.py"),
        proposed_start_line=1,
        proposed_end_line=5,
    )

    assert [collision["symbol_id"] for collision in result["symbol_collisions"]] == [
        "sample.py:Beta:1",
        "sample.py:alpha:4",
    ]
