from pathlib import Path

import pytest

from src.build_dcg_facts import build_dcg_facts
from src.consumer_bridge import build_structural_facts, run_structural_query
from src.query_interface import run_query


def test_consumer_bridge(tmp_path: Path) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text(
        "import os\n\n"
        "def foo():\n"
        "    return os.getcwd()\n",
        encoding="utf-8",
    )

    assert build_structural_facts(tmp_path) == build_dcg_facts(tmp_path)
    assert run_structural_query(
        tmp_path, "file_dependencies", file_path=Path("sample.py")
    ) == run_query(tmp_path, "file_dependencies", file_path=Path("sample.py"))

    with pytest.raises(ValueError, match="Unknown query type: unknown"):
        run_structural_query(tmp_path, "unknown")
