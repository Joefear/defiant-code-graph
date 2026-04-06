from pathlib import Path

from src.query_analyze_patch_targets import query_analyze_patch_targets


def test_query_analyze_patch_targets_maps_single_symbol_touch(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n\n"
        "def bar():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    patch_text = (
        "diff --git a/sample.py b/sample.py\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "@@ -1,2 +1,2 @@\n"
        "-    return 1\n"
        "+    return 3\n"
    )

    result = query_analyze_patch_targets(tmp_path, patch_text)

    assert result == {
        "patch_format": "unified_diff",
        "file_targets": [
            {
                "resolved_file_path": "sample.py",
                "old_file_path": "sample.py",
                "new_file_path": "sample.py",
                "change_kind": "modified",
                "known_file": True,
                "changed_ranges": [
                    {"old_start": 1, "old_count": 2, "new_start": 1, "new_count": 2}
                ],
                "symbol_touches": [
                    {
                        "symbol_id": "sample.py:foo:1",
                        "symbol_name": "foo",
                        "symbol_kind": "function",
                        "span": {"start_line": 1, "end_line": 2},
                        "evidence_basis": "patch_hunk_line_overlap",
                        "precision": "symbol",
                    }
                ],
                "file_touch_evidence": None,
            }
        ],
    }


def test_query_analyze_patch_targets_maps_multiple_symbols_in_one_file(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "def foo():\n"
        "    return 1\n\n"
        "def bar():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    patch_text = (
        "diff --git a/sample.py b/sample.py\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "@@ -1,5 +1,5 @@\n"
        "-    return 1\n"
        "+    return 3\n"
        "-    return 2\n"
        "+    return 4\n"
    )

    result = query_analyze_patch_targets(tmp_path, patch_text)

    assert [touch["symbol_id"] for touch in result["file_targets"][0]["symbol_touches"]] == [
        "sample.py:foo:1",
        "sample.py:bar:4",
    ]
    assert result["file_targets"][0]["file_touch_evidence"] is None


def test_query_analyze_patch_targets_reports_file_level_touch_when_no_symbol_overlap(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "import os\n\n"
        "def foo():\n"
        "    return os.getcwd()\n",
        encoding="utf-8",
    )

    patch_text = (
        "diff --git a/sample.py b/sample.py\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-import os\n"
        "+import sys\n"
    )

    result = query_analyze_patch_targets(tmp_path, patch_text)

    assert result["file_targets"][0]["symbol_touches"] == []
    assert result["file_targets"][0]["file_touch_evidence"] == {
        "file_path": "sample.py",
        "evidence_basis": "unified_diff_hunks",
        "precision": "file",
    }


def test_query_analyze_patch_targets_reports_unknown_out_of_repo_file(
    tmp_path: Path,
) -> None:
    patch_text = (
        "diff --git a/missing.py b/missing.py\n"
        "--- a/missing.py\n"
        "+++ b/missing.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-x = 1\n"
        "+x = 2\n"
    )

    result = query_analyze_patch_targets(tmp_path, patch_text)

    assert result["file_targets"] == [
        {
            "resolved_file_path": "missing.py",
            "old_file_path": "missing.py",
            "new_file_path": "missing.py",
            "change_kind": "modified",
            "known_file": False,
            "changed_ranges": [
                {"old_start": 1, "old_count": 1, "new_start": 1, "new_count": 1}
            ],
            "symbol_touches": [],
            "file_touch_evidence": {
                "file_path": "missing.py",
                "evidence_basis": "unified_diff_hunks",
                "precision": "file",
            },
        }
    ]


def test_query_analyze_patch_targets_handles_new_and_deleted_files_honestly(
    tmp_path: Path,
) -> None:
    (tmp_path / "deleted.py").write_text("def foo():\n    return 1\n", encoding="utf-8")

    patch_text = (
        "diff --git a/new_file.py b/new_file.py\n"
        "--- /dev/null\n"
        "+++ b/new_file.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+def foo():\n"
        "+    return 1\n"
        "diff --git a/deleted.py b/deleted.py\n"
        "--- a/deleted.py\n"
        "+++ /dev/null\n"
        "@@ -1,2 +0,0 @@\n"
        "-def foo():\n"
        "-    return 1\n"
    )

    result = query_analyze_patch_targets(tmp_path, patch_text)

    assert result["file_targets"] == [
        {
            "resolved_file_path": "deleted.py",
            "old_file_path": "deleted.py",
            "new_file_path": None,
            "change_kind": "deleted",
            "known_file": True,
            "changed_ranges": [
                {"old_start": 1, "old_count": 2, "new_start": 0, "new_count": 0}
            ],
            "symbol_touches": [
                {
                    "symbol_id": "deleted.py:foo:1",
                    "symbol_name": "foo",
                    "symbol_kind": "function",
                    "span": {"start_line": 1, "end_line": 2},
                    "evidence_basis": "patch_hunk_line_overlap",
                    "precision": "symbol",
                }
            ],
            "file_touch_evidence": None,
        },
        {
            "resolved_file_path": "new_file.py",
            "old_file_path": None,
            "new_file_path": "new_file.py",
            "change_kind": "added",
            "known_file": False,
            "changed_ranges": [
                {"old_start": 0, "old_count": 0, "new_start": 1, "new_count": 2}
            ],
            "symbol_touches": [],
            "file_touch_evidence": {
                "file_path": "new_file.py",
                "evidence_basis": "unified_diff_hunks",
                "precision": "file",
            },
        },
    ]


def test_query_analyze_patch_targets_sorts_output_deterministically(
    tmp_path: Path,
) -> None:
    (tmp_path / "b.py").write_text("def beta():\n    return 2\n", encoding="utf-8")
    (tmp_path / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")

    patch_text = (
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n"
        "+++ b/b.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-def beta():\n"
        "+def beta():\n"
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-def alpha():\n"
        "+def alpha():\n"
    )

    result = query_analyze_patch_targets(tmp_path, patch_text)

    assert [target["resolved_file_path"] for target in result["file_targets"]] == [
        "a.py",
        "b.py",
    ]
