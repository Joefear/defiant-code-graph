from __future__ import annotations

from pathlib import Path

from src.python_parser import parse_python_symbols
from src.repo_scanner import scan_repository
from src.symbol_normalizer import normalize_symbols


def build_python_symbol_index(root: Path) -> list[dict[str, object]]:
    symbols: list[dict[str, object]] = []

    for file_path in scan_repository(root):
        if file_path.suffix != ".py":
            continue

        relative_file_path = file_path.relative_to(root)
        raw_symbols = parse_python_symbols(file_path)
        symbols.extend(normalize_symbols(relative_file_path, raw_symbols))

    return symbols
