from __future__ import annotations

from pathlib import Path

from src.code_graph_builder import build_python_symbol_index
from src.query_symbol_metadata import query_symbol_metadata


def query_related_symbols(root: Path, symbol_id: str) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "related_symbols": [],
        }

    metadata = metadata_result["metadata"]
    related_symbols: list[dict[str, object]] = []

    for symbol in build_python_symbol_index(root):
        if symbol["file_path"] != metadata["file_path"]:
            continue
        if symbol["symbol_id"] == symbol_id:
            continue
        related_symbols.append(symbol)

    return {
        "symbol_id": symbol_id,
        "found": True,
        "related_symbols": related_symbols,
    }
