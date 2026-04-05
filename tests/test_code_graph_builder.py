from pathlib import Path

from src.code_graph_builder import build_python_symbol_index


def test_build_python_symbol_index(tmp_path: Path) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text("def foo():\n    pass\n", encoding="utf-8")

    ignored_file = tmp_path / "notes.txt"
    ignored_file.write_text("ignore me\n", encoding="utf-8")

    symbols = build_python_symbol_index(tmp_path)

    assert len(symbols) == 1
    assert symbols[0]["symbol_name"] == "foo"
    assert symbols[0]["symbol_kind"] == "function"
    assert symbols[0]["symbol_id"] == "sample.py:foo:1"
