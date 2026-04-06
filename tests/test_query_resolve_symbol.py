from pathlib import Path

from src.query_resolve_symbol import query_resolve_symbol


def test_query_resolve_symbol(tmp_path: Path) -> None:
    file_b = tmp_path / "b.py"
    file_a = tmp_path / "a.py"

    file_b.write_text("def foo():\n    pass\n", encoding="utf-8")
    file_a.write_text("def foo():\n    pass\n\ndef foobar():\n    pass\n", encoding="utf-8")

    matches = query_resolve_symbol(tmp_path, "foo")
    second_matches = query_resolve_symbol(tmp_path, "foo")
    missing_matches = query_resolve_symbol(tmp_path, "bar")
    fuzzy_matches = query_resolve_symbol(tmp_path, "fo")

    assert matches == second_matches
    assert matches == {
        "query": "foo",
        "matches": [
            {
                "symbol_id": "a.py:foo:1",
                "symbol_name": "foo",
                "symbol_kind": "function",
                "file_path": "a.py",
                "start_line": 1,
                "end_line": 2,
            },
            {
                "symbol_id": "b.py:foo:1",
                "symbol_name": "foo",
                "symbol_kind": "function",
                "file_path": "b.py",
                "start_line": 1,
                "end_line": 2,
            },
        ],
    }
    assert missing_matches == {"query": "bar", "matches": []}
    assert fuzzy_matches == {"query": "fo", "matches": []}
