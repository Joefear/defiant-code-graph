from __future__ import annotations

from pathlib import Path

from src.code_graph_builder import build_python_symbol_index


def build_python_symbol_relationships(root: Path) -> list[dict[str, object]]:
    relationships: list[dict[str, object]] = []

    for symbol in build_python_symbol_index(root):
        relationships.append(
            {
                "symbol_id": symbol["symbol_id"],
                "file_path": symbol["file_path"],
            }
        )

    return sorted(
        relationships,
        key=lambda relationship: (
            str(relationship["file_path"]),
            str(relationship["symbol_id"]),
        ),
    )
