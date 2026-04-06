from pathlib import Path

from src.python_symbol_relationships import build_python_symbol_relationships


def test_build_python_symbol_relationships(tmp_path: Path) -> None:
    file_b = tmp_path / "b.py"
    file_a = tmp_path / "a.py"

    file_b.write_text("def beta():\n    pass\n", encoding="utf-8")
    file_a.write_text("def alpha():\n    pass\n", encoding="utf-8")

    relationships = build_python_symbol_relationships(tmp_path)

    assert relationships == [
        {
            "symbol_id": "a.py:alpha:1",
            "file_path": "a.py",
        },
        {
            "symbol_id": "b.py:beta:1",
            "file_path": "b.py",
        },
    ]
    assert "parent_symbol_id" not in relationships[0]
    assert "parent_symbol_id" not in relationships[1]
