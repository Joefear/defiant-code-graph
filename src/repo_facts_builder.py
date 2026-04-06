from __future__ import annotations

from pathlib import Path

from src.file_ownership_classifier import build_file_ownership_facts
from src.python_dependency_graph import build_python_dependency_graph
from src.python_file_facts import build_python_file_facts
from src.python_symbol_relationships import build_python_symbol_relationships
from src.repo_scanner import scan_repository


def build_python_repo_facts(root: Path) -> dict[str, object]:
    files: list[dict[str, object]] = []

    for file_path in scan_repository(root):
        if file_path.suffix != ".py":
            continue

        file_facts = build_python_file_facts(file_path)
        files.append(
            {
                **file_facts,
                "file_path": str(file_path.relative_to(root)),
            }
        )

    return {
        "repo_root": str(root),
        "files": files,
        "dependencies": build_python_dependency_graph(root),
        "ownership": build_file_ownership_facts(root),
        "symbol_relationships": build_python_symbol_relationships(root),
    }
