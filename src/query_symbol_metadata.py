from __future__ import annotations

from pathlib import Path

from src.code_graph_builder import build_python_symbol_index


def query_symbol_metadata(root: Path, symbol_id: str) -> dict[str, object]:
    for symbol in build_python_symbol_index(root):
        if symbol["symbol_id"] == symbol_id:
            return {
                "symbol_id": symbol_id,
                "found": True,
                "metadata": symbol,
            }

    return {
        "symbol_id": symbol_id,
        "found": False,
        "metadata": None,
    }
