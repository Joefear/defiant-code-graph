from pathlib import Path

from src.python_dependency_graph import build_python_dependency_graph


def test_build_python_dependency_graph(tmp_path: Path) -> None:
    file_b = tmp_path / "b.py"
    file_a = tmp_path / "a.py"

    file_b.write_text(
        "import sys\n"
        "import os\n"
        "import os\n"
        "from .local import helper\n"
        "from math import sqrt\n",
        encoding="utf-8",
    )
    file_a.write_text("from collections import deque\n", encoding="utf-8")

    dependencies = build_python_dependency_graph(tmp_path)

    assert dependencies == [
        {"file_path": "a.py", "depends_on": ["collections"]},
        {"file_path": "b.py", "depends_on": ["math", "os", "sys"]},
    ]
