from __future__ import annotations

from pathlib import Path

from src.query_find_dependencies import query_find_dependencies
from src.query_find_dependents import query_find_dependents
from src.query_symbol_metadata import query_symbol_metadata


def query_get_blast_radius(root: Path, symbol_id: str) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "blast_radius": None,
        }

    metadata = metadata_result["metadata"]
    dependencies_result = query_find_dependencies(root, symbol_id)
    dependents_result = query_find_dependents(root, symbol_id)

    dependencies = [
        {"module": dependency, "support": "file_dependency"}
        for dependency in dependencies_result["dependencies"]
    ]

    return {
        "symbol_id": symbol_id,
        "found": True,
        "blast_radius": {
            "target": {
                "symbol": metadata,
                "containing_file": {
                    "file_path": str(metadata["file_path"]),
                    "support": "symbol_metadata",
                },
                "support": "symbol_metadata",
            },
            "dependencies": dependencies,
            "dependents": dependents_result["dependents"],
        },
    }
