from __future__ import annotations

from pathlib import Path

from src.query_file_dependencies import query_file_dependencies
from src.query_symbol_metadata import query_symbol_metadata


def query_find_dependencies(root: Path, symbol_id: str) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "dependencies": [],
        }

    metadata = metadata_result["metadata"]
    file_dependencies = query_file_dependencies(root, Path(str(metadata["file_path"])))

    return {
        "symbol_id": symbol_id,
        "found": True,
        "dependencies": file_dependencies["depends_on"],
    }
