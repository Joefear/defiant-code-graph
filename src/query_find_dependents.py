from __future__ import annotations

from pathlib import Path

from src.python_dependency_graph import build_python_dependency_graph
from src.query_symbol_metadata import query_symbol_metadata


def _module_name_for_file(file_path: Path) -> str:
    parts = list(file_path.with_suffix("").parts)

    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def query_find_dependents(root: Path, symbol_id: str) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "dependents": [],
        }

    metadata = metadata_result["metadata"]
    target_module = _module_name_for_file(Path(str(metadata["file_path"])))

    dependents: list[dict[str, str]] = []

    if target_module:
        for dependency in build_python_dependency_graph(root):
            if target_module not in dependency["depends_on"]:
                continue

            dependents.append(
                {
                    "file_path": str(dependency["file_path"]),
                    "support": "file_dependency",
                }
            )

    return {
        "symbol_id": symbol_id,
        "found": True,
        "dependents": dependents,
    }
