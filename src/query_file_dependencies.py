from __future__ import annotations

from pathlib import Path

from src.python_dependency_graph import build_python_dependency_graph


def query_file_dependencies(root: Path, file_path: Path) -> dict[str, object]:
    relative_file_path = file_path

    if file_path.is_absolute():
        relative_file_path = file_path.relative_to(root)

    relative_file_path_string = str(relative_file_path)

    for dependency in build_python_dependency_graph(root):
        if dependency["file_path"] == relative_file_path_string:
            return {
                "file_path": relative_file_path_string,
                "depends_on": dependency["depends_on"],
            }

    return {
        "file_path": relative_file_path_string,
        "depends_on": [],
    }
