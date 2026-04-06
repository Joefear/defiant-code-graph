from pathlib import Path

from src.query_related_symbols import query_related_symbols


def test_query_related_symbols(tmp_path: Path) -> None:
    same_file = tmp_path / "module.py"
    other_file = tmp_path / "other.py"

    same_file.write_text(
        "def alpha():\n    pass\n\n\nclass Beta:\n    pass\n",
        encoding="utf-8",
    )
    other_file.write_text("def alpha():\n    pass\n", encoding="utf-8")

    result = query_related_symbols(tmp_path, "module.py:alpha:1")
    second_result = query_related_symbols(tmp_path, "module.py:alpha:1")
    missing_result = query_related_symbols(tmp_path, "module.py:missing:1")

    assert result == second_result
    assert result == {
        "symbol_id": "module.py:alpha:1",
        "found": True,
        "related_symbols": [
            {
                "symbol_id": "module.py:Beta:5",
                "symbol_name": "Beta",
                "symbol_kind": "class",
                "file_path": "module.py",
                "start_line": 5,
                "end_line": 6,
            }
        ],
    }
    assert missing_result == {
        "symbol_id": "module.py:missing:1",
        "found": False,
        "related_symbols": [],
    }
