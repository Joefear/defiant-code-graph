from pathlib import Path

from src.query_classify_change_type import query_classify_change_type


def test_query_classify_change_type_pure_additive_patch(tmp_path: Path) -> None:
    patch_text = (
        "diff --git a/new_file.py b/new_file.py\n"
        "--- /dev/null\n"
        "+++ b/new_file.py\n"
        "@@ -0,0 +1,2 @@\n"
        "+def foo():\n"
        "+    return 1\n"
    )

    result = query_classify_change_type(tmp_path, patch_text)

    assert result["classifications"] == ["additive"]
    assert result["per_file_classification"] == [
        {
            "file_path": "new_file.py",
            "change_kind": "added",
            "classifications": ["additive"],
            "evidence_summary": {
                "added_lines": 2,
                "deleted_lines": 0,
                "touched_symbol_count": 0,
                "touched_file_count": 1,
                "boundary_crossing_count": 0,
            },
        }
    ]


def test_query_classify_change_type_pure_destructive_patch(tmp_path: Path) -> None:
    (tmp_path / "gone.py").write_text("def foo():\n    return 1\n", encoding="utf-8")

    patch_text = (
        "diff --git a/gone.py b/gone.py\n"
        "--- a/gone.py\n"
        "+++ /dev/null\n"
        "@@ -1,2 +0,0 @@\n"
        "-def foo():\n"
        "-    return 1\n"
    )

    result = query_classify_change_type(tmp_path, patch_text)

    assert result["classifications"] == ["destructive"]
    assert result["per_file_classification"][0]["classifications"] == ["destructive"]


def test_query_classify_change_type_modifying_patch(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text("def foo():\n    return 1\n", encoding="utf-8")

    patch_text = (
        "diff --git a/sample.py b/sample.py\n"
        "--- a/sample.py\n"
        "+++ b/sample.py\n"
        "@@ -1,2 +1,2 @@\n"
        "-def foo():\n"
        "+def foo():\n"
        "-    return 1\n"
        "+    return 2\n"
    )

    result = query_classify_change_type(tmp_path, patch_text)

    assert result["classifications"] == ["modifying"]
    assert result["per_file_classification"][0]["classifications"] == ["modifying"]


def test_query_classify_change_type_structural_path_changed_patch(
    tmp_path: Path,
) -> None:
    (tmp_path / "old.py").write_text("def foo():\n    return 1\n", encoding="utf-8")

    patch_text = (
        "diff --git a/old.py b/new.py\n"
        "--- a/old.py\n"
        "+++ b/new.py\n"
        "@@ -1,2 +1,2 @@\n"
        "-def foo():\n"
        "+def foo():\n"
        "-    return 1\n"
        "+    return 1\n"
    )

    result = query_classify_change_type(tmp_path, patch_text)

    assert result["classifications"] == ["modifying", "structural"]
    assert result["per_file_classification"][0]["classifications"] == [
        "modifying",
        "structural",
    ]


def test_query_classify_change_type_multi_file_patch_is_structural(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.py").write_text("def alpha():\n    return 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("def beta():\n    return 2\n", encoding="utf-8")

    patch_text = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-def alpha():\n"
        "+def alpha():\n"
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n"
        "+++ b/b.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-def beta():\n"
        "+def beta():\n"
    )

    result = query_classify_change_type(tmp_path, patch_text)

    assert result["classifications"] == ["modifying", "structural"]
    assert all(
        "structural" in item["classifications"] for item in result["per_file_classification"]
    )


def test_query_classify_change_type_ordering_is_deterministic(tmp_path: Path) -> None:
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

    result = query_classify_change_type(tmp_path, patch_text)

    assert [item["file_path"] for item in result["per_file_classification"]] == [
        "a.py",
        "b.py",
    ]
