from __future__ import annotations

from pathlib import Path

from src.code_graph_builder import build_python_symbol_index
from src.query_symbol_metadata import query_symbol_metadata
from src.repo_scanner import scan_repository


def _known_repo_files(root: Path) -> set[str]:
    return {file_path.relative_to(root).as_posix() for file_path in scan_repository(root)}


def _symbols_for_file(root: Path, file_path: str) -> list[dict[str, object]]:
    symbols = [
        symbol
        for symbol in build_python_symbol_index(root)
        if str(symbol["file_path"]) == file_path
    ]
    symbols.sort(key=lambda item: (int(item["start_line"]), str(item["symbol_id"])))
    return symbols


def query_find_insertion_points_for_file(root: Path, file_path: Path) -> dict[str, object]:
    relative_file_path = file_path

    if file_path.is_absolute():
        relative_file_path = file_path.relative_to(root)

    normalized_file_path = relative_file_path.as_posix()
    if normalized_file_path not in _known_repo_files(root):
        return {
            "found": False,
            "file_path": normalized_file_path,
            "candidates": [],
        }

    symbols = _symbols_for_file(root, normalized_file_path)
    candidates: list[dict[str, object]] = []

    if not symbols:
        candidates.append(
            {
                "candidate_type": "file",
                "start_line": None,
                "end_line": None,
                "anchor_before_symbol_id": None,
                "anchor_after_symbol_id": None,
                "container_symbol_id": None,
                "precision": "file",
                "evidence_basis": "known_repo_file",
            }
        )
        return {
            "found": True,
            "file_path": normalized_file_path,
            "candidates": candidates,
        }

    first_symbol = symbols[0]
    last_symbol = symbols[-1]
    candidates.append(
        {
            "candidate_type": "before_first_top_level_symbol",
            "start_line": int(first_symbol["start_line"]),
            "end_line": int(first_symbol["start_line"]),
            "anchor_before_symbol_id": None,
            "anchor_after_symbol_id": str(first_symbol["symbol_id"]),
            "container_symbol_id": None,
            "precision": "line",
            "evidence_basis": "top_level_symbol_order",
        }
    )

    for previous_symbol, next_symbol in zip(symbols, symbols[1:]):
        candidates.append(
            {
                "candidate_type": "between_top_level_symbols",
                "start_line": int(previous_symbol["end_line"]),
                "end_line": int(next_symbol["start_line"]),
                "anchor_before_symbol_id": str(previous_symbol["symbol_id"]),
                "anchor_after_symbol_id": str(next_symbol["symbol_id"]),
                "container_symbol_id": None,
                "precision": "region",
                "evidence_basis": "top_level_symbol_order",
            }
        )

    candidates.append(
        {
            "candidate_type": "after_last_top_level_symbol",
            "start_line": int(last_symbol["end_line"]) + 1,
            "end_line": int(last_symbol["end_line"]) + 1,
            "anchor_before_symbol_id": str(last_symbol["symbol_id"]),
            "anchor_after_symbol_id": None,
            "container_symbol_id": None,
            "precision": "line",
            "evidence_basis": "top_level_symbol_span",
        }
    )

    return {
        "found": True,
        "file_path": normalized_file_path,
        "candidates": candidates,
    }


def query_find_insertion_points(
    root: Path, *, file_path: Path | None = None, symbol_id: str | None = None
) -> dict[str, object]:
    if symbol_id is not None:
        metadata_result = query_symbol_metadata(root, symbol_id)

        if not metadata_result["found"]:
            return {
                "found": False,
                "file_path": None,
                "symbol_id": symbol_id,
                "candidates": [],
            }

        metadata = metadata_result["metadata"]
        return {
            "found": True,
            "file_path": str(metadata["file_path"]),
            "symbol_id": symbol_id,
            "candidates": [
                {
                    "candidate_type": "inside_container_symbol",
                    "start_line": int(metadata["start_line"]),
                    "end_line": int(metadata["end_line"]),
                    "anchor_before_symbol_id": None,
                    "anchor_after_symbol_id": None,
                    "container_symbol_id": symbol_id,
                    "precision": "region",
                    "evidence_basis": "symbol_span",
                }
            ],
        }

    if file_path is None:
        raise ValueError("Either file_path or symbol_id is required")

    return query_find_insertion_points_for_file(root, file_path)
