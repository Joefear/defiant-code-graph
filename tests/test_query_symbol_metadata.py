from pathlib import Path

from src.query_symbol_metadata import query_symbol_metadata


def test_query_symbol_metadata(tmp_path: Path) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text("def foo():\n    pass\n", encoding="utf-8")

    symbol_id = "sample.py:foo:1"
    metadata = query_symbol_metadata(tmp_path, symbol_id)
    second_metadata = query_symbol_metadata(tmp_path, symbol_id)
    missing_metadata = query_symbol_metadata(tmp_path, "sample.py:bar:1")

    assert metadata == second_metadata
    assert metadata == {
        "symbol_id": symbol_id,
        "found": True,
        "metadata": {
            "symbol_id": symbol_id,
            "symbol_name": "foo",
            "symbol_kind": "function",
            "file_path": "sample.py",
            "start_line": 1,
            "end_line": 2,
        },
    }
    assert missing_metadata == {
        "symbol_id": "sample.py:bar:1",
        "found": False,
        "metadata": None,
    }
    assert "parent_symbol_id" not in metadata["metadata"]
