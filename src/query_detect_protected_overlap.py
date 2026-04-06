from __future__ import annotations

from pathlib import Path

from src.file_ownership_classifier import build_file_ownership_facts
from src.query_symbol_metadata import query_symbol_metadata
from src.repo_scanner import scan_repository


PROTECTED_OWNERSHIP_CLASSES = frozenset(
    {"locked", "governed", "critical", "policy_sensitive"}
)


def _normalize_span(span: dict[str, object] | None) -> dict[str, int | None] | None:
    if span is None:
        return None

    return {
        "start_line": int(span["start_line"]) if span["start_line"] is not None else None,
        "end_line": int(span["end_line"]) if span["end_line"] is not None else None,
    }


def _ownership_map(root: Path) -> dict[str, str]:
    return {
        Path(str(fact["file_path"])).as_posix(): str(fact["ownership"])
        for fact in build_file_ownership_facts(root)
    }


def _known_repo_files(root: Path) -> set[str]:
    return {file_path.relative_to(root).as_posix() for file_path in scan_repository(root)}


def _protected_targets_for_file(
    file_path: str,
    ownership_by_file: dict[str, str],
) -> list[dict[str, str]]:
    ownership = ownership_by_file.get(file_path)

    if ownership not in PROTECTED_OWNERSHIP_CLASSES:
        return []

    return [
        {
            "file_path": file_path,
            "protection_class": ownership,
            "evidence_basis": "file_ownership_facts",
            "precision": "file",
        }
    ]


def query_detect_protected_overlap_for_file(
    root: Path,
    file_path: Path,
    span: dict[str, object] | None = None,
) -> dict[str, object]:
    relative_file_path = file_path

    if file_path.is_absolute():
        relative_file_path = file_path.relative_to(root)

    normalized_file_path = relative_file_path.as_posix()
    known_files = _known_repo_files(root)
    ownership_by_file = _ownership_map(root)
    requested_span = _normalize_span(span)

    if normalized_file_path not in known_files:
        return {
            "file_path": normalized_file_path,
            "found": False,
            "requested_span": requested_span,
            "overlap_detected": False,
            "protected_targets": [],
            "precision": None,
        }

    protected_targets = _protected_targets_for_file(normalized_file_path, ownership_by_file)

    return {
        "file_path": normalized_file_path,
        "found": True,
        "requested_span": requested_span,
        "overlap_detected": bool(protected_targets),
        "protected_targets": protected_targets,
        "precision": "file",
    }


def query_detect_protected_overlap(
    root: Path,
    symbol_id: str,
    span: dict[str, object] | None = None,
) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "target": None,
            "requested_span": _normalize_span(span),
            "overlap_detected": False,
            "protected_targets": [],
            "precision": None,
        }

    metadata = metadata_result["metadata"]
    requested_span = _normalize_span(span)
    symbol_span = {
        "start_line": int(metadata["start_line"]),
        "end_line": int(metadata["end_line"]),
    }
    file_result = query_detect_protected_overlap_for_file(
        root,
        Path(str(metadata["file_path"])),
        span=requested_span,
    )

    return {
        "symbol_id": symbol_id,
        "found": True,
        "target": {
            "file_path": str(metadata["file_path"]),
            "symbol_name": str(metadata["symbol_name"]),
            "symbol_kind": str(metadata["symbol_kind"]),
            "symbol_span": symbol_span,
        },
        "requested_span": requested_span,
        "overlap_detected": bool(file_result["protected_targets"]),
        "protected_targets": file_result["protected_targets"],
        "precision": "file",
    }
