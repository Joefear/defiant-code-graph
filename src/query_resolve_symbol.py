from __future__ import annotations

from pathlib import Path

from src.code_graph_builder import build_python_symbol_index


def query_resolve_symbol(root: Path, symbol_name: str) -> dict[str, object]:
    matches: list[dict[str, object]] = []

    for symbol in build_python_symbol_index(root):
        if symbol["symbol_name"] == symbol_name:
            matches.append(symbol)

    return {
        "query": symbol_name,
        "matches": matches,
    }
