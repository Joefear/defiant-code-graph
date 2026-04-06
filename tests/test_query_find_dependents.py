from pathlib import Path

from src.query_find_dependents import query_find_dependents


def test_query_find_dependents(tmp_path: Path) -> None:
    package_dir = tmp_path / "pkg"
    package_dir.mkdir()

    (package_dir / "__init__.py").write_text("", encoding="utf-8")
    (package_dir / "provider.py").write_text(
        "def foo():\n"
        "    return 1\n",
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
    (tmp_path / "z_unrelated.py").write_text(
        "import os\n",
        encoding="utf-8",
    )

    result = query_find_dependents(tmp_path, "pkg/provider.py:foo:1")
    second_result = query_find_dependents(tmp_path, "pkg/provider.py:foo:1")
    missing_result = query_find_dependents(tmp_path, "pkg/provider.py:missing:1")

    assert result == second_result
    assert result == {
        "symbol_id": "pkg/provider.py:foo:1",
        "found": True,
        "dependents": [
            {"file_path": "a_consumer.py", "support": "file_dependency"},
            {"file_path": "b_consumer.py", "support": "file_dependency"},
        ],
    }
    assert missing_result == {
        "symbol_id": "pkg/provider.py:missing:1",
        "found": False,
        "dependents": [],
    }
