from pathlib import Path

from src.query_symbol_source import query_symbol_source


def test_query_symbol_source(tmp_path: Path) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text(
        "def foo():\n"
        "    value = 1\n"
        "    return value\n",
        encoding="utf-8",
    )

    symbol_id = "sample.py:foo:1"
    result = query_symbol_source(tmp_path, symbol_id)
    second_result = query_symbol_source(tmp_path, symbol_id)
    missing_result = query_symbol_source(tmp_path, "sample.py:bar:1")

    assert result == second_result
    assert result == {
        "symbol_id": symbol_id,
        "found": True,
        "source": "def foo():\n    value = 1\n    return value\n",
        "file_path": "sample.py",
        "span": {
            "start_line": 1,
            "end_line": 3,
        },
    }
    assert missing_result == {
        "symbol_id": "sample.py:bar:1",
        "found": False,
        "source": None,
        "file_path": None,
        "span": None,
    }
