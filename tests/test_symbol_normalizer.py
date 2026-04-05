from pathlib import Path

from src.symbol_normalizer import normalize_symbols


def test_normalize_symbols() -> None:
    raw_symbols = [
        {
            "symbol_name": "foo",
            "symbol_kind": "function",
            "start_line": 1,
            "end_line": 2,
        }
    ]

    symbols = normalize_symbols(Path("example.py"), raw_symbols)

    assert len(symbols) == 1
    assert symbols[0]["symbol_id"] == "example.py:foo:1"
    assert symbols[0]["symbol_name"] == "foo"
    assert symbols[0]["symbol_kind"] == "function"
    assert symbols[0]["file_path"] == "example.py"
    assert symbols[0]["start_line"] == 1
    assert symbols[0]["end_line"] == 2
