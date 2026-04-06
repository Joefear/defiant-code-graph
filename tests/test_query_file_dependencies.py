from pathlib import Path

from src.query_file_dependencies import query_file_dependencies


def test_query_file_dependencies(tmp_path: Path) -> None:
    file_b = tmp_path / "b.py"
    file_a = tmp_path / "a.py"

    file_b.write_text(
        "import sys\n"
        "import os\n"
        "from math import sqrt\n",
        encoding="utf-8",
    )
    file_a.write_text("def alpha():\n    pass\n", encoding="utf-8")

    known_dependencies = query_file_dependencies(tmp_path, Path("b.py"))
    second_known_dependencies = query_file_dependencies(tmp_path, Path("b.py"))
    no_dependency_result = query_file_dependencies(tmp_path, Path("a.py"))
    unknown_result = query_file_dependencies(tmp_path, Path("missing.py"))

    assert known_dependencies == second_known_dependencies
    assert known_dependencies == {
        "file_path": "b.py",
        "depends_on": ["math", "os", "sys"],
    }
    assert no_dependency_result == {"file_path": "a.py", "depends_on": []}
    assert unknown_result == {"file_path": "missing.py", "depends_on": []}
