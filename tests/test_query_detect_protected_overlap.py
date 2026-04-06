from pathlib import Path

from src.query_detect_protected_overlap import (
    query_detect_protected_overlap,
    query_detect_protected_overlap_for_file,
)


def test_query_detect_protected_overlap_reports_locked_symbol_overlap(
    tmp_path: Path,
) -> None:
    (tmp_path / "locked.py").write_text(
        "# @locked\n"
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_detect_protected_overlap(tmp_path, "locked.py:foo:2")

    assert result == {
        "symbol_id": "locked.py:foo:2",
        "found": True,
        "target": {
            "file_path": "locked.py",
            "symbol_name": "foo",
            "symbol_kind": "function",
            "symbol_span": {"start_line": 2, "end_line": 3},
        },
        "requested_span": None,
        "overlap_detected": True,
        "protected_targets": [
            {
                "file_path": "locked.py",
                "protection_class": "locked",
                "evidence_basis": "file_ownership_facts",
                "precision": "file",
            }
        ],
        "precision": "file",
    }


def test_query_detect_protected_overlap_reports_supported_protection_classes(
    tmp_path: Path,
) -> None:
    (tmp_path / "governed.py").write_text("# @governed\n", encoding="utf-8")
    (tmp_path / "critical.py").write_text("# @critical\n", encoding="utf-8")
    (tmp_path / ".env").write_text("SECRET_KEY=x\n", encoding="utf-8")

    governed_result = query_detect_protected_overlap_for_file(
        tmp_path, Path("governed.py")
    )
    critical_result = query_detect_protected_overlap_for_file(
        tmp_path, Path("critical.py")
    )
    policy_result = query_detect_protected_overlap_for_file(tmp_path, Path(".env"))

    assert governed_result["protected_targets"][0]["protection_class"] == "governed"
    assert critical_result["protected_targets"][0]["protection_class"] == "critical"
    assert policy_result["protected_targets"][0]["protection_class"] == "policy_sensitive"


def test_query_detect_protected_overlap_no_overlap_on_unprotected_target(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_detect_protected_overlap(tmp_path, "sample.py:foo:1")

    assert result == {
        "symbol_id": "sample.py:foo:1",
        "found": True,
        "target": {
            "file_path": "sample.py",
            "symbol_name": "foo",
            "symbol_kind": "function",
            "symbol_span": {"start_line": 1, "end_line": 2},
        },
        "requested_span": None,
        "overlap_detected": False,
        "protected_targets": [],
        "precision": "file",
    }


def test_query_detect_protected_overlap_is_explicitly_file_level_when_span_requested(
    tmp_path: Path,
) -> None:
    (tmp_path / "critical.py").write_text(
        "# ownership: critical\n"
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )

    result = query_detect_protected_overlap(
        tmp_path,
        "critical.py:foo:2",
        span={"start_line": 2, "end_line": 2},
    )

    assert result == {
        "symbol_id": "critical.py:foo:2",
        "found": True,
        "target": {
            "file_path": "critical.py",
            "symbol_name": "foo",
            "symbol_kind": "function",
            "symbol_span": {"start_line": 2, "end_line": 3},
        },
        "requested_span": {"start_line": 2, "end_line": 2},
        "overlap_detected": True,
        "protected_targets": [
            {
                "file_path": "critical.py",
                "protection_class": "critical",
                "evidence_basis": "file_ownership_facts",
                "precision": "file",
            }
        ],
        "precision": "file",
    }


def test_query_detect_protected_overlap_for_file_missing_target_stays_empty(
    tmp_path: Path,
) -> None:
    result = query_detect_protected_overlap_for_file(
        tmp_path,
        Path("missing.py"),
        span={"start_line": 1, "end_line": 1},
    )

    assert result == {
        "file_path": "missing.py",
        "found": False,
        "requested_span": {"start_line": 1, "end_line": 1},
        "overlap_detected": False,
        "protected_targets": [],
        "precision": None,
    }


def test_query_detect_protected_overlap_missing_symbol_stays_empty(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    result = query_detect_protected_overlap(tmp_path, "sample.py:missing:1")

    assert result == {
        "symbol_id": "sample.py:missing:1",
        "found": False,
        "target": None,
        "requested_span": None,
        "overlap_detected": False,
        "protected_targets": [],
        "precision": None,
    }
