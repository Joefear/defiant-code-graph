from pathlib import Path

from src.query_file_outline import query_file_outline


def test_query_file_outline(tmp_path: Path) -> None:
    known_file = tmp_path / "module.py"
    known_file.write_text(
        "class Beta:\n    pass\n\n\ndef alpha():\n    pass\n",
        encoding="utf-8",
    )

    outline = query_file_outline(tmp_path, Path("module.py"))
    second_outline = query_file_outline(tmp_path, Path("module.py"))
    missing_outline = query_file_outline(tmp_path, Path("missing.py"))

    assert outline == second_outline
    assert outline == {
        "file_path": "module.py",
        "symbols": [
            {
                "symbol_name": "Beta",
                "symbol_kind": "class",
                "start_line": 1,
                "end_line": 2,
            },
            {
                "symbol_name": "alpha",
                "symbol_kind": "function",
                "start_line": 5,
                "end_line": 6,
            },
        ],
    }
    assert missing_outline == {"file_path": "missing.py", "symbols": []}
    assert "symbol_id" not in outline["symbols"][0]
