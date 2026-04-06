from pathlib import Path

from src.query_find_dependencies import query_find_dependencies


def test_query_find_dependencies(tmp_path: Path) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text(
        "import os\n"
        "from math import sqrt\n\n"
        "def foo():\n"
        "    return os.getcwd()\n",
        encoding="utf-8",
    )

    result = query_find_dependencies(tmp_path, "sample.py:foo:4")
    second_result = query_find_dependencies(tmp_path, "sample.py:foo:4")
    missing_result = query_find_dependencies(tmp_path, "sample.py:bar:4")

    assert result == second_result
    assert result == {
        "symbol_id": "sample.py:foo:4",
        "found": True,
        "dependencies": ["math", "os"],
    }
    assert missing_result == {
        "symbol_id": "sample.py:bar:4",
        "found": False,
        "dependencies": [],
    }
