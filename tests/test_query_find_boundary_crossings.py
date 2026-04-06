from pathlib import Path

from src.query_find_boundary_crossings import (
    query_find_boundary_crossings,
    query_find_boundary_crossings_for_file,
)


def test_query_find_boundary_crossings_same_top_level_only_reports_file_crossing(
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
    (package_dir / "consumer.py").write_text(
        "from pkg.provider import foo\n",
        encoding="utf-8",
    )

    result = query_find_boundary_crossings(tmp_path, "pkg/provider.py:foo:1")

    assert result == {
        "symbol_id": "pkg/provider.py:foo:1",
        "found": True,
        "crossings": [
            {
                "source_symbol_id": "pkg/provider.py:foo:1",
                "source_file_path": "pkg/provider.py",
                "related_target": "pkg/consumer.py",
                "relation_kind": "dependent",
                "boundary_type": "file",
                "from_value": "pkg/provider.py",
                "to_value": "pkg/consumer.py",
                "evidence_basis": "file_dependency_graph",
            },
        ],
    }


def test_query_find_boundary_crossings_reports_cross_file_and_top_level_package(
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

    result = query_find_boundary_crossings(tmp_path, "pkg/provider.py:foo:1")

    assert result == {
        "symbol_id": "pkg/provider.py:foo:1",
        "found": True,
        "crossings": [
            {
                "source_symbol_id": "pkg/provider.py:foo:1",
                "source_file_path": "pkg/provider.py",
                "related_target": "consumer.py",
                "relation_kind": "dependent",
                "boundary_type": "file",
                "from_value": "pkg/provider.py",
                "to_value": "consumer.py",
                "evidence_basis": "file_dependency_graph",
            },
            {
                "source_symbol_id": "pkg/provider.py:foo:1",
                "source_file_path": "pkg/provider.py",
                "related_target": "consumer.py",
                "relation_kind": "dependent",
                "boundary_type": "top_level_package",
                "from_value": "pkg",
                "to_value": "consumer",
                "evidence_basis": "normalized_file_paths",
            },
        ],
    }


def test_query_find_boundary_crossings_reports_ownership_crossing_when_supported(
    tmp_path: Path,
) -> None:
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()

    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "provider.py").write_text(
        "# @locked\n"
        "def foo():\n"
        "    return 1\n",
        encoding="utf-8",
    )
    (tmp_path / "consumer.py").write_text(
        "# ownership: governed\n"
        "from pkg.provider import foo\n",
        encoding="utf-8",
    )

    result = query_find_boundary_crossings(tmp_path, "pkg/provider.py:foo:2")

    assert result == {
        "symbol_id": "pkg/provider.py:foo:2",
        "found": True,
        "crossings": [
            {
                "source_symbol_id": "pkg/provider.py:foo:2",
                "source_file_path": "pkg/provider.py",
                "related_target": "consumer.py",
                "relation_kind": "dependent",
                "boundary_type": "file",
                "from_value": "pkg/provider.py",
                "to_value": "consumer.py",
                "evidence_basis": "file_dependency_graph",
            },
            {
                "source_symbol_id": "pkg/provider.py:foo:2",
                "source_file_path": "pkg/provider.py",
                "related_target": "consumer.py",
                "relation_kind": "dependent",
                "boundary_type": "top_level_package",
                "from_value": "pkg",
                "to_value": "consumer",
                "evidence_basis": "normalized_file_paths",
            },
            {
                "source_symbol_id": "pkg/provider.py:foo:2",
                "source_file_path": "pkg/provider.py",
                "related_target": "consumer.py",
                "relation_kind": "dependent",
                "boundary_type": "ownership",
                "from_value": "locked",
                "to_value": "governed",
                "evidence_basis": "file_ownership_facts",
            },
        ],
    }


def test_query_find_boundary_crossings_ambiguous_external_dependency_stays_empty(
    tmp_path: Path,
) -> None:
    (tmp_path / "sample.py").write_text(
        "import os\n\n"
        "def foo():\n"
        "    return os.getcwd()\n",
        encoding="utf-8",
    )

    result = query_find_boundary_crossings(tmp_path, "sample.py:foo:3")

    assert result == {
        "symbol_id": "sample.py:foo:3",
        "found": True,
        "crossings": [],
    }


def test_query_find_boundary_crossings_for_file_reports_crossings(
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

    result = query_find_boundary_crossings_for_file(tmp_path, Path("consumer.py"))

    assert result == {
        "file_path": "consumer.py",
        "found": True,
        "crossings": [
            {
                "related_target": "pkg/provider.py",
                "relation_kind": "dependency",
                "boundary_type": "file",
                "from_value": "consumer.py",
                "to_value": "pkg/provider.py",
                "evidence_basis": "file_dependency_graph",
            },
            {
                "related_target": "pkg/provider.py",
                "relation_kind": "dependency",
                "boundary_type": "top_level_package",
                "from_value": "consumer",
                "to_value": "pkg",
                "evidence_basis": "normalized_file_paths",
            },
        ],
    }


def test_query_find_boundary_crossings_missing_symbol(tmp_path: Path) -> None:
    (tmp_path / "sample.py").write_text("def foo():\n    pass\n", encoding="utf-8")

    result = query_find_boundary_crossings(tmp_path, "sample.py:missing:1")

    assert result == {
        "symbol_id": "sample.py:missing:1",
        "found": False,
        "crossings": [],
    }
