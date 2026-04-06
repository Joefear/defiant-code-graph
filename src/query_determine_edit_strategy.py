from __future__ import annotations

from pathlib import Path

from src.query_detect_generation_collision import query_detect_generation_collision
from src.query_find_insertion_points import query_find_insertion_points


def query_determine_edit_strategy(
    root: Path,
    *,
    proposed_start_line: int,
    proposed_end_line: int,
    file_path: Path | None = None,
    symbol_id: str | None = None,
) -> dict[str, object]:
    insertion_result = query_find_insertion_points(
        root, file_path=file_path, symbol_id=symbol_id
    )
    collision_result = query_detect_generation_collision(
        root,
        file_path=file_path,
        symbol_id=symbol_id,
        proposed_start_line=proposed_start_line,
        proposed_end_line=proposed_end_line,
    )

    resolved_file_path = collision_result["file_path"]
    resolved_symbol_id = collision_result["symbol_id"]

    if not insertion_result["found"] or not collision_result["found"]:
        return {
            "found": False,
            "file_path": resolved_file_path,
            "symbol_id": resolved_symbol_id,
            "proposed_region": {
                "start_line": proposed_start_line,
                "end_line": proposed_end_line,
            },
            "strategy": "unknown",
            "supporting_facts": {
                "insertion_candidates": insertion_result["candidates"],
                "collision_result": collision_result,
            },
            "precision": None,
            "evidence_basis": [],
        }

    if collision_result["symbol_collisions"]:
        return {
            "found": True,
            "file_path": resolved_file_path,
            "symbol_id": resolved_symbol_id,
            "proposed_region": {
                "start_line": proposed_start_line,
                "end_line": proposed_end_line,
            },
            "strategy": "rewrite",
            "supporting_facts": {
                "insertion_candidates": insertion_result["candidates"],
                "collision_result": collision_result,
            },
            "precision": "line",
            "evidence_basis": ["symbol_span_overlap"],
        }

    if resolved_symbol_id is not None:
        has_container_candidate = any(
            candidate["candidate_type"] == "inside_container_symbol"
            for candidate in insertion_result["candidates"]
        )
        if has_container_candidate and not collision_result["collision_detected"]:
            return {
                "found": True,
                "file_path": resolved_file_path,
                "symbol_id": resolved_symbol_id,
                "proposed_region": {
                    "start_line": proposed_start_line,
                    "end_line": proposed_end_line,
                },
                "strategy": "extend",
                "supporting_facts": {
                    "insertion_candidates": insertion_result["candidates"],
                    "collision_result": collision_result,
                },
                "precision": "region",
                "evidence_basis": ["symbol_span"],
            }

    if collision_result["protected_collisions"]:
        return {
            "found": True,
            "file_path": resolved_file_path,
            "symbol_id": resolved_symbol_id,
            "proposed_region": {
                "start_line": proposed_start_line,
                "end_line": proposed_end_line,
            },
            "strategy": "unknown",
            "supporting_facts": {
                "insertion_candidates": insertion_result["candidates"],
                "collision_result": collision_result,
            },
            "precision": collision_result["precision"],
            "evidence_basis": collision_result["evidence_basis"],
        }

    if insertion_result["candidates"]:
        return {
            "found": True,
            "file_path": resolved_file_path,
            "symbol_id": resolved_symbol_id,
            "proposed_region": {
                "start_line": proposed_start_line,
                "end_line": proposed_end_line,
            },
            "strategy": "insert_new",
            "supporting_facts": {
                "insertion_candidates": insertion_result["candidates"],
                "collision_result": collision_result,
            },
            "precision": insertion_result["candidates"][0]["precision"],
            "evidence_basis": sorted(
                {
                    candidate["evidence_basis"]
                    for candidate in insertion_result["candidates"]
                }
            ),
        }

    return {
        "found": True,
        "file_path": resolved_file_path,
        "symbol_id": resolved_symbol_id,
        "proposed_region": {
            "start_line": proposed_start_line,
            "end_line": proposed_end_line,
        },
        "strategy": "unknown",
        "supporting_facts": {
            "insertion_candidates": insertion_result["candidates"],
            "collision_result": collision_result,
        },
        "precision": None,
        "evidence_basis": [],
    }
