from pathlib import Path

from src.query_get_blast_radius import query_get_blast_radius


def test_query_get_blast_radius(tmp_path: Path) -> None:
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()

    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "provider.py").write_text(
        "import os\n"
        "from math import sqrt\n\n"
        "def foo():\n"
        "    return os.getcwd() + str(sqrt(4))\n",
        encoding="utf-8",
    )
    (tmp_path / "a_consumer.py").write_text(
        "import pkg.provider\n",
        encoding="utf-8",
    )
    (tmp_path / "b_consumer.py").write_text(
        "from pkg.provider import foo\n",
        encoding="utf-8",
    )
    (tmp_path / "c_transitive.py").write_text(
        "import a_consumer\n",
        encoding="utf-8",
    )

    result = query_get_blast_radius(tmp_path, "pkg/provider.py:foo:4")
    second_result = query_get_blast_radius(tmp_path, "pkg/provider.py:foo:4")
    missing_result = query_get_blast_radius(tmp_path, "pkg/provider.py:missing:4")

    assert result == second_result
    assert result == {
        "symbol_id": "pkg/provider.py:foo:4",
        "found": True,
        "blast_radius": {
            "target": {
                "symbol": {
                    "symbol_id": "pkg/provider.py:foo:4",
                    "symbol_name": "foo",
                    "symbol_kind": "function",
                    "file_path": "pkg/provider.py",
                    "start_line": 4,
                    "end_line": 5,
                },
                "containing_file": {
                    "file_path": "pkg/provider.py",
                    "support": "symbol_metadata",
                },
                "support": "symbol_metadata",
            },
            "dependencies": [
                {"module": "math", "support": "file_dependency"},
                {"module": "os", "support": "file_dependency"},
            ],
            "dependents": [
                {"file_path": "a_consumer.py", "support": "file_dependency"},
                {"file_path": "b_consumer.py", "support": "file_dependency"},
            ],
        },
    }
    assert missing_result == {
        "symbol_id": "pkg/provider.py:missing:4",
        "found": False,
        "blast_radius": None,
    }
