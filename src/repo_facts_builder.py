from __future__ import annotations

from pathlib import Path

from src.python_file_facts import build_python_file_facts
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
    }
