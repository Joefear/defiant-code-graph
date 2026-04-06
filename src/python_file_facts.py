from __future__ import annotations

from pathlib import Path

from src.python_dependency_extractor import extract_python_imports
from src.python_parser import parse_python_symbols


def build_python_file_facts(file_path: Path) -> dict[str, object]:
    return {
        "file_path": str(file_path),
        "symbols": parse_python_symbols(file_path),
        "imports": extract_python_imports(file_path),
    }
