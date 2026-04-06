from pathlib import Path

from src.query_compare_intent_to_patch import query_compare_intent_to_patch


def test_query_compare_intent_to_patch_stays_within_intended_symbol(
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
        "@@ -1,2 +1,2 @@\n"
        "-    return 1\n"
        "+    return 3\n"
    )

    result = query_compare_intent_to_patch(
        tmp_path, {"symbol_id": "sample.py:foo:1"}, patch_text
    )

    assert result["matched_intended_target"] is True
    assert result["actual_touched_files"] == ["sample.py"]
    assert result["actual_touched_symbols"] == ["sample.py:foo:1"]
    assert result["out_of_scope_files"] == []
    assert result["out_of_scope_symbols"] == []
    assert result["scope_expansion_detected"] is False
    assert result["precision"] == "symbol"
    assert result["precision_mismatch_detected"] is False


def test_query_compare_intent_to_patch_detects_extra_symbol_in_same_file(
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

    result = query_compare_intent_to_patch(
        tmp_path, {"symbol_id": "sample.py:foo:1"}, patch_text
    )

    assert result["out_of_scope_files"] == []
    assert result["out_of_scope_symbols"] == ["sample.py:bar:4"]
    assert result["scope_expansion_detected"] is True


def test_query_compare_intent_to_patch_stays_within_intended_file(
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

    result = query_compare_intent_to_patch(
        tmp_path, {"file_path": "sample.py"}, patch_text
    )

    assert result["matched_intended_target"] is True
    assert result["actual_touched_files"] == ["sample.py"]
    assert result["out_of_scope_files"] == []
    assert result["scope_expansion_detected"] is False
    assert result["precision"] == "file"


def test_query_compare_intent_to_patch_detects_extra_file_expansion(
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

    result = query_compare_intent_to_patch(tmp_path, {"file_path": "a.py"}, patch_text)

    assert result["actual_touched_files"] == ["a.py", "b.py"]
    assert result["out_of_scope_files"] == ["b.py"]
    assert result["scope_expansion_detected"] is True


def test_query_compare_intent_to_patch_detects_boundary_expansion(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()
    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "provider.py").write_text(
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "consumer.py").write_text(
        "from pkg.provider import foo\n",
        encoding="utf-8",
    )

    patch_text = (
        "diff --git a/pkg/provider.py b/pkg/provider.py\n"
        "--- a/pkg/provider.py\n"
        "+++ b/pkg/provider.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-def foo():\n"
        "+def foo():\n"
        "diff --git a/consumer.py b/consumer.py\n"
        "--- a/consumer.py\n"
        "+++ b/consumer.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-from pkg.provider import foo\n"
        "+from pkg.provider import foo\n"
    )

    result = query_compare_intent_to_patch(
        tmp_path, {"file_path": "pkg/provider.py"}, patch_text
    )

    assert result["boundary_expansion_detected"] is True
    assert result["out_of_scope_files"] == ["consumer.py"]


def test_query_compare_intent_to_patch_detects_protected_expansion(
    tmp_path: Path,
) -> None:
    (tmp_path / "manual.py").write_text("def foo():\n    return 1\n", encoding="utf-8")
    (tmp_path / "locked.py").write_text(
        "# @locked\n"
        "def bar():\n"
        "    return 2\n",
        encoding="utf-8",
    )

    patch_text = (
        "diff --git a/manual.py b/manual.py\n"
        "--- a/manual.py\n"
        "+++ b/manual.py\n"
        "@@ -1,1 +1,1 @@\n"
        "-def foo():\n"
        "+def foo():\n"
        "diff --git a/locked.py b/locked.py\n"
        "--- a/locked.py\n"
        "+++ b/locked.py\n"
        "@@ -2,1 +2,1 @@\n"
        "-def bar():\n"
        "+def bar():\n"
    )

    result = query_compare_intent_to_patch(tmp_path, {"file_path": "manual.py"}, patch_text)

    assert result["protected_expansion_detected"] is True
    assert result["out_of_scope_files"] == ["locked.py"]


def test_query_compare_intent_to_patch_handles_symbol_precision_mismatch_honestly(
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

    result = query_compare_intent_to_patch(
        tmp_path, {"symbol_id": "sample.py:foo:3"}, patch_text
    )

    assert result["actual_touched_files"] == ["sample.py"]
    assert result["actual_touched_symbols"] == []
    assert result["precision_mismatch_detected"] is True
    assert result["scope_expansion_detected"] is None
