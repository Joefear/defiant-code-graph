from pathlib import Path

from src.python_file_facts import build_python_file_facts


def test_build_python_file_facts(tmp_path: Path) -> None:
    temp_file = tmp_path / "sample.py"
    temp_file.write_text("import os\n\ndef foo():\n    pass\n", encoding="utf-8")

    facts = build_python_file_facts(temp_file)

    assert facts["file_path"] == str(temp_file)
    assert facts["imports"] == ["os"]
    assert len(facts["symbols"]) == 1
    assert facts["symbols"][0]["symbol_name"] == "foo"
    assert facts["symbols"][0]["symbol_kind"] == "function"
