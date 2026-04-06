from pathlib import Path

from src.query_analyze_patch_impact import query_analyze_patch_impact


def test_query_analyze_patch_impact_reports_symbol_level_direct_impact(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()

    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "provider.py").write_text(
        "# @locked\n"
        "import math\n\n"
        "def foo():\n"
        "    return math.sqrt(4)\n",
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
        "@@ -4,2 +4,2 @@\n"
        "-def foo():\n"
        "+def foo():\n"
        "-    return math.sqrt(4)\n"
        "+    return math.sqrt(9)\n"
    )

    result = query_analyze_patch_impact(tmp_path, patch_text)

    assert result["patch_format"] == "unified_diff"
    assert result["direct_targets"]["file_targets"][0]["resolved_file_path"] == "pkg/provider.py"
    assert result["file_impact"] == []
    assert result["symbol_impact"] == [
        {
            "symbol_id": "pkg/provider.py:foo:4",
            "file_path": "pkg/provider.py",
            "change_kind": "modified",
            "changed_ranges": [
                {"old_start": 4, "old_count": 2, "new_start": 4, "new_count": 2}
            ],
            "direct_dependencies": ["math"],
            "direct_dependents": [
                {"file_path": "consumer.py", "support": "file_dependency"}
            ],
            "boundary_crossings": [
                {
                    "source_symbol_id": "pkg/provider.py:foo:4",
                    "source_file_path": "pkg/provider.py",
                    "related_target": "consumer.py",
                    "relation_kind": "dependent",
                    "boundary_type": "file",
                    "from_value": "pkg/provider.py",
                    "to_value": "consumer.py",
                    "evidence_basis": "file_dependency_graph",
                },
                {
                    "source_symbol_id": "pkg/provider.py:foo:4",
                    "source_file_path": "pkg/provider.py",
                    "related_target": "consumer.py",
                    "relation_kind": "dependent",
                    "boundary_type": "top_level_package",
                    "from_value": "pkg",
                    "to_value": "consumer",
                    "evidence_basis": "normalized_file_paths",
                },
                {
                    "source_symbol_id": "pkg/provider.py:foo:4",
                    "source_file_path": "pkg/provider.py",
                    "related_target": "consumer.py",
                    "relation_kind": "dependent",
                    "boundary_type": "ownership",
                    "from_value": "locked",
                    "to_value": "manual",
                    "evidence_basis": "file_ownership_facts",
                },
            ],
            "protected_overlap": [
                {
                    "file_path": "pkg/provider.py",
                    "protection_class": "locked",
                    "evidence_basis": "file_ownership_facts",
                    "precision": "file",
                }
            ],
            "precision": "symbol",
        }
    ]


def test_query_analyze_patch_impact_reports_file_level_only_touch(
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

    result = query_analyze_patch_impact(tmp_path, patch_text)

    assert result["symbol_impact"] == []
    assert result["file_impact"] == [
        {
            "file_path": "sample.py",
            "change_kind": "modified",
            "known_file": True,
            "changed_ranges": [
                {"old_start": 1, "old_count": 1, "new_start": 1, "new_count": 1}
            ],
            "direct_dependencies": ["os"],
            "direct_dependents": [],
            "boundary_crossings": [],
            "protected_overlap": [],
            "file_touch_evidence": {
                "file_path": "sample.py",
                "evidence_basis": "unified_diff_hunks",
                "precision": "file",
            },
            "precision": "file",
        }
    ]


def test_query_analyze_patch_impact_handles_multiple_symbols_and_files(
    tmp_path: Path,
) -> None:
    (tmp_path / "a.py").write_text(
        "def alpha():\n"
        "    return 1\n\n"
        "def beta():\n"
        "    return 2\n",
        encoding="utf-8",
    )
    (tmp_path / "b.py").write_text(
        "import a\n\n"
        "def gamma():\n"
        "    return a.alpha()\n",
        encoding="utf-8",
    )

    patch_text = (
        "diff --git a/b.py b/b.py\n"
        "--- a/b.py\n"
        "+++ b/b.py\n"
        "@@ -3,2 +3,2 @@\n"
        "-def gamma():\n"
        "+def gamma():\n"
        "-    return a.alpha()\n"
        "+    return a.beta()\n"
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@ -4,2 +4,2 @@\n"
        "-def beta():\n"
        "+def beta():\n"
        "-    return 2\n"
        "+    return 3\n"
    )

    result = query_analyze_patch_impact(tmp_path, patch_text)

    assert [item["symbol_id"] for item in result["symbol_impact"]] == [
        "a.py:beta:4",
        "b.py:gamma:3",
    ]
    assert result["file_impact"] == []


def test_query_analyze_patch_impact_handles_unknown_out_of_repo_file_honestly(
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

    result = query_analyze_patch_impact(tmp_path, patch_text)

    assert result["symbol_impact"] == []
    assert result["file_impact"] == [
        {
            "file_path": "missing.py",
            "change_kind": "modified",
            "known_file": False,
            "changed_ranges": [
                {"old_start": 1, "old_count": 1, "new_start": 1, "new_count": 1}
            ],
            "direct_dependencies": [],
            "direct_dependents": [],
            "boundary_crossings": [],
            "protected_overlap": [],
            "file_touch_evidence": {
                "file_path": "missing.py",
                "evidence_basis": "unified_diff_hunks",
                "precision": "file",
            },
            "precision": "file",
        }
    ]


def test_query_analyze_patch_impact_sorts_output_deterministically(
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

    result = query_analyze_patch_impact(tmp_path, patch_text)

    assert [item["symbol_id"] for item in result["symbol_impact"]] == [
        "a.py:alpha:1",
        "b.py:beta:1",
    ]
    assert result["file_impact"] == []


def test_query_analyze_patch_impact_stays_direct_only_for_symbol_dependencies(
    tmp_path: Path,
) -> None:
    (tmp_path / "provider.py").write_text(
        "import os\n"
        "from math import sqrt\n\n"
        "def foo():\n"
        "    return os.getcwd(), sqrt(4)\n",
        encoding="utf-8",
    )
    (tmp_path / "consumer.py").write_text("from provider import foo\n", encoding="utf-8")
    (tmp_path / "transitive.py").write_text("import consumer\n", encoding="utf-8")

    patch_text = (
        "diff --git a/provider.py b/provider.py\n"
        "--- a/provider.py\n"
        "+++ b/provider.py\n"
        "@@ -4,2 +4,2 @@\n"
        "-def foo():\n"
        "+def foo():\n"
        "-    return os.getcwd(), sqrt(4)\n"
        "+    return os.getcwd(), sqrt(9)\n"
    )

    result = query_analyze_patch_impact(tmp_path, patch_text)

    assert result["symbol_impact"][0]["direct_dependencies"] == ["math", "os"]
    assert result["symbol_impact"][0]["direct_dependents"] == [
        {"file_path": "consumer.py", "support": "file_dependency"}
    ]
