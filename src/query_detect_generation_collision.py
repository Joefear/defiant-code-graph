from __future__ import annotations

from pathlib import Path

from src.code_graph_builder import build_python_symbol_index
from src.query_detect_protected_overlap import query_detect_protected_overlap_for_file
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


def _range_overlaps(
    start_line: int, end_line: int, symbol_start: int, symbol_end: int
) -> bool:
    return not (end_line < symbol_start or start_line > symbol_end)


def _overall_precision(
    symbol_collisions: list[dict[str, object]], protected_collisions: list[dict[str, object]]
) -> str | None:
    if symbol_collisions and protected_collisions:
        return "mixed"
    if symbol_collisions:
        return "line"
    if protected_collisions:
        return "file"
    return None


def query_detect_generation_collision(
    root: Path,
    *,
    proposed_start_line: int,
    proposed_end_line: int,
    file_path: Path | None = None,
    symbol_id: str | None = None,
) -> dict[str, object]:
    resolved_symbol_id = symbol_id
    normalized_file_path: str | None = None

    if symbol_id is not None:
        metadata_result = query_symbol_metadata(root, symbol_id)
        if not metadata_result["found"]:
            return {
                "found": False,
                "file_path": None,
                "symbol_id": symbol_id,
                "proposed_region": {
                    "start_line": proposed_start_line,
                    "end_line": proposed_end_line,
                },
                "collision_detected": False,
                "symbol_collisions": [],
                "protected_collisions": [],
                "precision": None,
                "evidence_basis": [],
            }

        normalized_file_path = str(metadata_result["metadata"]["file_path"])
    elif file_path is not None:
        relative_file_path = file_path
        if file_path.is_absolute():
            relative_file_path = file_path.relative_to(root)
        normalized_file_path = relative_file_path.as_posix()
    else:
        raise ValueError("Either file_path or symbol_id is required")

    if normalized_file_path not in _known_repo_files(root):
        return {
            "found": False,
            "file_path": normalized_file_path,
            "symbol_id": resolved_symbol_id,
            "proposed_region": {
                "start_line": proposed_start_line,
                "end_line": proposed_end_line,
            },
            "collision_detected": False,
            "symbol_collisions": [],
            "protected_collisions": [],
            "precision": None,
            "evidence_basis": [],
        }

    symbol_collisions: list[dict[str, object]] = []
    for symbol in _symbols_for_file(root, normalized_file_path):
        if _range_overlaps(
            proposed_start_line,
            proposed_end_line,
            int(symbol["start_line"]),
            int(symbol["end_line"]),
        ):
            symbol_collisions.append(
                {
                    "symbol_id": str(symbol["symbol_id"]),
                    "symbol_name": str(symbol["symbol_name"]),
                    "symbol_kind": str(symbol["symbol_kind"]),
                    "span": {
                        "start_line": int(symbol["start_line"]),
                        "end_line": int(symbol["end_line"]),
                    },
                    "precision": "line",
                    "evidence_basis": "symbol_span_overlap",
                }
            )

    protected_result = query_detect_protected_overlap_for_file(
        root,
        Path(normalized_file_path),
        span={
            "start_line": proposed_start_line,
            "end_line": proposed_end_line,
        },
    )
    protected_collisions = [
        {
            **protected_target,
            "requested_region": {
                "start_line": proposed_start_line,
                "end_line": proposed_end_line,
            },
        }
        for protected_target in protected_result["protected_targets"]
    ]
    precision = _overall_precision(symbol_collisions, protected_collisions)
    evidence_basis = sorted(
        {
            *(collision["evidence_basis"] for collision in symbol_collisions),
            *(collision["evidence_basis"] for collision in protected_collisions),
        }
    )

    return {
        "found": True,
        "file_path": normalized_file_path,
        "symbol_id": resolved_symbol_id,
        "proposed_region": {
            "start_line": proposed_start_line,
            "end_line": proposed_end_line,
        },
        "collision_detected": bool(symbol_collisions or protected_collisions),
        "symbol_collisions": symbol_collisions,
        "protected_collisions": protected_collisions,
        "precision": precision,
        "evidence_basis": evidence_basis,
    }
