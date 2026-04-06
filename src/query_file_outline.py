from __future__ import annotations

from pathlib import Path

from src.python_file_facts import build_python_file_facts


def query_file_outline(root: Path, file_path: Path) -> dict[str, object]:
    relative_file_path = file_path
    absolute_file_path = root / file_path

    if file_path.is_absolute():
        relative_file_path = file_path.relative_to(root)
        absolute_file_path = file_path

    if absolute_file_path.suffix != ".py" or not absolute_file_path.is_file():
        return {
            "file_path": str(relative_file_path),
            "symbols": [],
        }

    file_facts = build_python_file_facts(absolute_file_path)
    return {
        "file_path": str(relative_file_path),
        "symbols": file_facts["symbols"],
    }
