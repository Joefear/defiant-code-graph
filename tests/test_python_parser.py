from pathlib import Path

from src.python_parser import parse_python_symbols


def test_parse_python_symbols(tmp_path: Path) -> None:
    temp_file = tmp_path / "sample.py"
    temp_file.write_text(
        "def foo():\n"
        "    pass\n\n"
        "async def bar():\n"
        "    pass\n\n"
        "class Baz:\n"
        "    pass\n",
        encoding="utf-8",
    )

    symbols = parse_python_symbols(temp_file)

    assert len(symbols) == 3
    assert [symbol["symbol_name"] for symbol in symbols] == ["foo", "bar", "Baz"]
    assert [symbol["symbol_kind"] for symbol in symbols] == [
        "function",
        "async_function",
        "class",
    ]