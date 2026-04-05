from __future__ import annotations

import ast
from pathlib import Path


def parse_python_symbols(file_path: Path) -> list[dict[str, object]]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))

    symbols: list[dict[str, object]] = []

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            symbol_kind = "function"
        elif isinstance(node, ast.AsyncFunctionDef):
            symbol_kind = "async_function"
        elif isinstance(node, ast.ClassDef):
            symbol_kind = "class"
        else:
            continue

        symbols.append(
            {
                "symbol_name": node.name,
                "symbol_kind": symbol_kind,
                "start_line": node.lineno,
                "end_line": (
                    node.end_lineno if node.end_lineno is not None else node.lineno
                ),
            }
        )

    return symbols