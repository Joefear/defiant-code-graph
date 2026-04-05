from pathlib import Path

from src.python_dependency_extractor import extract_python_imports


def test_extract_python_imports(tmp_path: Path) -> None:
    temp_file = tmp_path / "sample.py"
    temp_file.write_text(
        "import os\n"
        "import sys\n"
        "from math import sqrt\n"
        "from collections import deque\n"
        "from .utils import helper\n",
        encoding="utf-8",
    )

    imports = extract_python_imports(temp_file)

    assert imports == ["os", "sys", "math", "collections"]
