from __future__ import annotations

from pathlib import Path

from src.query_file_dependencies import query_file_dependencies
from src.query_file_outline import query_file_outline
from src.query_related_symbols import query_related_symbols
from src.query_resolve_symbol import query_resolve_symbol
from src.query_symbol_metadata import query_symbol_metadata
from src.query_symbol_source import query_symbol_source


def run_query(root: Path, query_type: str, **kwargs: object) -> dict[str, object]:
    if query_type == "file_outline":
        return query_file_outline(root, kwargs["file_path"])
    if query_type == "file_dependencies":
        return query_file_dependencies(root, kwargs["file_path"])
    if query_type == "symbol_metadata":
        return query_symbol_metadata(root, kwargs["symbol_id"])
    if query_type == "resolve_symbol":
        return query_resolve_symbol(root, kwargs["symbol_name"])
    if query_type == "symbol_source":
        return query_symbol_source(root, kwargs["symbol_id"])
    if query_type == "related_symbols":
        return query_related_symbols(root, kwargs["symbol_id"])

    raise ValueError(f"Unknown query type: {query_type}")


def run_file_outline_query(root: Path, file_path: Path) -> dict[str, object]:
    return query_file_outline(root, file_path)


def run_file_dependencies_query(root: Path, file_path: Path) -> dict[str, object]:
    return query_file_dependencies(root, file_path)


def run_symbol_metadata_query(root: Path, symbol_id: str) -> dict[str, object]:
    return query_symbol_metadata(root, symbol_id)


def run_resolve_symbol_query(root: Path, symbol_name: str) -> dict[str, object]:
    return query_resolve_symbol(root, symbol_name)


def run_symbol_source_query(root: Path, symbol_id: str) -> dict[str, object]:
    return query_symbol_source(root, symbol_id)


def run_related_symbols_query(root: Path, symbol_id: str) -> dict[str, object]:
    return query_related_symbols(root, symbol_id)
