from pathlib import Path

import pytest

from src.query_detect_protected_overlap import query_detect_protected_overlap
from src.query_file_dependencies import query_file_dependencies
from src.query_find_boundary_crossings import query_find_boundary_crossings
from src.query_file_outline import query_file_outline
from src.query_interface import run_query
from src.query_related_symbols import query_related_symbols
from src.query_resolve_symbol import query_resolve_symbol
from src.query_symbol_metadata import query_symbol_metadata
from src.query_symbol_source import query_symbol_source


def test_query_interface(tmp_path: Path) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text(
        "import os\n\n"
        "def foo():\n"
        "    pass\n\n"
        "class Bar:\n"
        "    pass\n",
        encoding="utf-8",
    )

    assert run_query(tmp_path, "file_outline", file_path=Path("sample.py")) == query_file_outline(
        tmp_path, Path("sample.py")
    )
    assert run_query(
        tmp_path, "file_dependencies", file_path=Path("sample.py")
    ) == query_file_dependencies(tmp_path, Path("sample.py"))
    assert run_query(
        tmp_path, "detect_protected_overlap", symbol_id="sample.py:foo:3"
    ) == query_detect_protected_overlap(tmp_path, "sample.py:foo:3")
    assert run_query(
        tmp_path, "symbol_metadata", symbol_id="sample.py:foo:3"
    ) == query_symbol_metadata(tmp_path, "sample.py:foo:3")
    assert run_query(
        tmp_path, "resolve_symbol", symbol_name="foo"
    ) == query_resolve_symbol(tmp_path, "foo")
    assert run_query(
        tmp_path, "symbol_source", symbol_id="sample.py:foo:3"
    ) == query_symbol_source(tmp_path, "sample.py:foo:3")
    assert run_query(
        tmp_path, "related_symbols", symbol_id="sample.py:foo:3"
    ) == query_related_symbols(tmp_path, "sample.py:foo:3")
    assert run_query(
        tmp_path, "find_boundary_crossings", symbol_id="sample.py:foo:3"
    ) == query_find_boundary_crossings(tmp_path, "sample.py:foo:3")

    with pytest.raises(ValueError, match="Unknown query type: unknown"):
        run_query(tmp_path, "unknown")
