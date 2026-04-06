from __future__ import annotations

from pathlib import Path

from src.python_dependency_extractor import extract_python_imports
from src.repo_scanner import scan_repository


def build_python_dependency_graph(root: Path) -> list[dict[str, object]]:
    dependencies: list[dict[str, object]] = []

    for file_path in scan_repository(root):
        if file_path.suffix != ".py":
            continue

        dependencies.append(
            {
                "file_path": str(file_path.relative_to(root)),
                "depends_on": sorted(set(extract_python_imports(file_path))),
            }
        )

    return dependencies
