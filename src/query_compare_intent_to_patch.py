from __future__ import annotations

from pathlib import Path

from src.query_analyze_patch_impact import query_analyze_patch_impact
from src.query_detect_protected_overlap import (
    query_detect_protected_overlap,
    query_detect_protected_overlap_for_file,
)
from src.query_find_boundary_crossings import (
    query_find_boundary_crossings,
    query_find_boundary_crossings_for_file,
)
from src.query_symbol_metadata import query_symbol_metadata


def _normalize_intent(intent: dict[str, object]) -> dict[str, str]:
    if "symbol_id" in intent:
        return {"symbol_id": str(intent["symbol_id"])}
    if "file_path" in intent:
        return {"file_path": Path(str(intent["file_path"])).as_posix()}
    raise ValueError("Intent must include either symbol_id or file_path")


def _normalize_boundary_records(records: list[dict[str, object]]) -> list[dict[str, str]]:
    normalized = {
        (
            str(record["boundary_type"]),
            str(record["relation_kind"]),
            str(record["from_value"]),
            str(record["to_value"]),
            str(record["related_target"]),
            str(record["evidence_basis"]),
        ): {
            "boundary_type": str(record["boundary_type"]),
            "relation_kind": str(record["relation_kind"]),
            "from_value": str(record["from_value"]),
            "to_value": str(record["to_value"]),
            "related_target": str(record["related_target"]),
            "evidence_basis": str(record["evidence_basis"]),
        }
        for record in records
    }

    return [normalized[key] for key in sorted(normalized)]


def _normalize_protected_records(records: list[dict[str, object]]) -> list[dict[str, str]]:
    normalized = {
        (
            str(record["file_path"]),
            str(record["protection_class"]),
            str(record["evidence_basis"]),
            str(record["precision"]),
        ): {
            "file_path": str(record["file_path"]),
            "protection_class": str(record["protection_class"]),
            "evidence_basis": str(record["evidence_basis"]),
            "precision": str(record["precision"]),
        }
        for record in records
    }

    return [normalized[key] for key in sorted(normalized)]


def _boundary_set(records: list[dict[str, str]]) -> set[tuple[str, ...]]:
    return {
        (
            record["boundary_type"],
            record["relation_kind"],
            record["from_value"],
            record["to_value"],
            record["related_target"],
            record["evidence_basis"],
        )
        for record in records
    }


def _protected_set(records: list[dict[str, str]]) -> set[tuple[str, ...]]:
    return {
        (
            record["file_path"],
            record["protection_class"],
            record["evidence_basis"],
            record["precision"],
        )
        for record in records
    }


def query_compare_intent_to_patch(
    root: Path, intent: dict[str, object], patch_text: str
) -> dict[str, object]:
    normalized_intent = _normalize_intent(intent)
    patch_impact = query_analyze_patch_impact(root, patch_text)
    actual_touched_files = sorted(
        {
            str(file_target["resolved_file_path"])
            for file_target in patch_impact["direct_targets"]["file_targets"]
            if file_target["resolved_file_path"] is not None
        }
    )
    actual_touched_symbols = sorted(
        {str(symbol_impact["symbol_id"]) for symbol_impact in patch_impact["symbol_impact"]}
    )

    actual_boundary_footprint = _normalize_boundary_records(
        [
            crossing
            for symbol_impact in patch_impact["symbol_impact"]
            for crossing in symbol_impact["boundary_crossings"]
        ]
        + [
            crossing
            for file_impact in patch_impact["file_impact"]
            for crossing in file_impact["boundary_crossings"]
        ]
    )
    actual_protected_targets = _normalize_protected_records(
        [
            protected
            for symbol_impact in patch_impact["symbol_impact"]
            for protected in symbol_impact["protected_overlap"]
        ]
        + [
            protected
            for file_impact in patch_impact["file_impact"]
            for protected in file_impact["protected_overlap"]
        ]
    )

    if "symbol_id" in normalized_intent:
        symbol_id = normalized_intent["symbol_id"]
        metadata_result = query_symbol_metadata(root, symbol_id)
        matched = bool(metadata_result["found"])

        if not matched:
            return {
                "intent": normalized_intent,
                "patch_format": patch_impact["patch_format"],
                "matched_intended_target": False,
                "actual_touched_files": actual_touched_files,
                "actual_touched_symbols": actual_touched_symbols,
                "out_of_scope_files": [],
                "out_of_scope_symbols": [],
                "boundary_expansion_detected": None,
                "protected_expansion_detected": None,
                "scope_expansion_detected": None,
                "precision": "unknown",
                "precision_mismatch_detected": False,
                "evidence_summaries": {
                    "intended_files": [],
                    "intended_symbols": [],
                    "intended_boundary_footprint": [],
                    "actual_boundary_footprint": actual_boundary_footprint,
                    "intended_protected_targets": [],
                    "actual_protected_targets": actual_protected_targets,
                },
            }

        intended_file_path = str(metadata_result["metadata"]["file_path"])
        intended_symbols = [symbol_id]
        intended_files = [intended_file_path]
        intended_boundary_footprint = _normalize_boundary_records(
            query_find_boundary_crossings(root, symbol_id)["crossings"]
        )
        intended_protected_targets = _normalize_protected_records(
            query_detect_protected_overlap(root, symbol_id)["protected_targets"]
        )
        out_of_scope_files = sorted(
            file_path for file_path in actual_touched_files if file_path != intended_file_path
        )
        out_of_scope_symbols = sorted(
            actual_symbol
            for actual_symbol in actual_touched_symbols
            if actual_symbol != symbol_id
        )
        precision_mismatch_detected = any(
            file_impact["file_path"] == intended_file_path
            for file_impact in patch_impact["file_impact"]
        )
        scope_expansion_detected: bool | None
        if precision_mismatch_detected and not actual_touched_symbols:
            scope_expansion_detected = None
        else:
            scope_expansion_detected = bool(out_of_scope_files or out_of_scope_symbols)

        return {
            "intent": normalized_intent,
            "patch_format": patch_impact["patch_format"],
            "matched_intended_target": True,
            "actual_touched_files": actual_touched_files,
            "actual_touched_symbols": actual_touched_symbols,
            "out_of_scope_files": out_of_scope_files,
            "out_of_scope_symbols": out_of_scope_symbols,
            "boundary_expansion_detected": not _boundary_set(
                actual_boundary_footprint
            ).issubset(_boundary_set(intended_boundary_footprint)),
            "protected_expansion_detected": not _protected_set(
                actual_protected_targets
            ).issubset(_protected_set(intended_protected_targets)),
            "scope_expansion_detected": scope_expansion_detected,
            "precision": "symbol",
            "precision_mismatch_detected": precision_mismatch_detected,
            "evidence_summaries": {
                "intended_files": intended_files,
                "intended_symbols": intended_symbols,
                "intended_boundary_footprint": intended_boundary_footprint,
                "actual_boundary_footprint": actual_boundary_footprint,
                "intended_protected_targets": intended_protected_targets,
                "actual_protected_targets": actual_protected_targets,
            },
        }

    file_path = normalized_intent["file_path"]
    file_protected_result = query_detect_protected_overlap_for_file(root, Path(file_path))
    matched = bool(file_protected_result["found"])

    if not matched:
        return {
            "intent": normalized_intent,
            "patch_format": patch_impact["patch_format"],
            "matched_intended_target": False,
            "actual_touched_files": actual_touched_files,
            "actual_touched_symbols": actual_touched_symbols,
            "out_of_scope_files": [],
            "out_of_scope_symbols": [],
            "boundary_expansion_detected": None,
            "protected_expansion_detected": None,
            "scope_expansion_detected": None,
            "precision": "unknown",
            "precision_mismatch_detected": False,
            "evidence_summaries": {
                "intended_files": [],
                "intended_symbols": [],
                "intended_boundary_footprint": [],
                "actual_boundary_footprint": actual_boundary_footprint,
                "intended_protected_targets": [],
                "actual_protected_targets": actual_protected_targets,
            },
        }

    intended_boundary_footprint = _normalize_boundary_records(
        query_find_boundary_crossings_for_file(root, Path(file_path))["crossings"]
    )
    intended_protected_targets = _normalize_protected_records(
        file_protected_result["protected_targets"]
    )
    out_of_scope_files = sorted(
        actual_file for actual_file in actual_touched_files if actual_file != file_path
    )

    return {
        "intent": normalized_intent,
        "patch_format": patch_impact["patch_format"],
        "matched_intended_target": True,
        "actual_touched_files": actual_touched_files,
        "actual_touched_symbols": actual_touched_symbols,
        "out_of_scope_files": out_of_scope_files,
        "out_of_scope_symbols": [],
        "boundary_expansion_detected": not _boundary_set(actual_boundary_footprint).issubset(
            _boundary_set(intended_boundary_footprint)
        ),
        "protected_expansion_detected": not _protected_set(actual_protected_targets).issubset(
            _protected_set(intended_protected_targets)
        ),
        "scope_expansion_detected": bool(out_of_scope_files),
        "precision": "file",
        "precision_mismatch_detected": False,
        "evidence_summaries": {
            "intended_files": [file_path],
            "intended_symbols": [],
            "intended_boundary_footprint": intended_boundary_footprint,
            "actual_boundary_footprint": actual_boundary_footprint,
            "intended_protected_targets": intended_protected_targets,
            "actual_protected_targets": actual_protected_targets,
        },
    }
