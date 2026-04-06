from __future__ import annotations

from pathlib import Path

from src.python_dependency_graph import build_python_dependency_graph
from src.query_analyze_patch_targets import query_analyze_patch_targets
from src.query_detect_protected_overlap import (
    query_detect_protected_overlap,
    query_detect_protected_overlap_for_file,
)
from src.query_file_dependencies import query_file_dependencies
from src.query_find_boundary_crossings import (
    query_find_boundary_crossings,
    query_find_boundary_crossings_for_file,
)
from src.query_find_dependencies import query_find_dependencies
from src.query_find_dependents import query_find_dependents


def _module_name_for_file(file_path: Path) -> str:
    parts = list(file_path.with_suffix("").parts)

    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def _query_file_dependents(root: Path, file_path: str) -> list[dict[str, str]]:
    target_module = _module_name_for_file(Path(file_path))
    dependents: list[dict[str, str]] = []

    if not target_module:
        return dependents

    for dependency in build_python_dependency_graph(root):
        if target_module not in dependency["depends_on"]:
            continue

        dependents.append(
            {
                "file_path": str(dependency["file_path"]),
                "support": "file_dependency",
            }
        )

    return sorted(dependents, key=lambda item: item["file_path"])


def query_analyze_patch_impact(root: Path, patch_text: str) -> dict[str, object]:
    direct_targets = query_analyze_patch_targets(root, patch_text)
    symbol_impact: list[dict[str, object]] = []
    file_impact: list[dict[str, object]] = []

    for file_target in direct_targets["file_targets"]:
        symbol_touches = file_target["symbol_touches"]

        for symbol_touch in symbol_touches:
            symbol_id = str(symbol_touch["symbol_id"])
            symbol_impact.append(
                {
                    "symbol_id": symbol_id,
                    "file_path": str(file_target["resolved_file_path"]),
                    "change_kind": str(file_target["change_kind"]),
                    "changed_ranges": file_target["changed_ranges"],
                    "direct_dependencies": query_find_dependencies(root, symbol_id)[
                        "dependencies"
                    ],
                    "direct_dependents": query_find_dependents(root, symbol_id)[
                        "dependents"
                    ],
                    "boundary_crossings": query_find_boundary_crossings(root, symbol_id)[
                        "crossings"
                    ],
                    "protected_overlap": query_detect_protected_overlap(root, symbol_id)[
                        "protected_targets"
                    ],
                    "precision": "symbol",
                }
            )

        if symbol_touches:
            continue

        resolved_file_path = file_target["resolved_file_path"]
        if resolved_file_path is None:
            file_impact.append(
                {
                    "file_path": None,
                    "change_kind": str(file_target["change_kind"]),
                    "known_file": bool(file_target["known_file"]),
                    "changed_ranges": file_target["changed_ranges"],
                    "direct_dependencies": [],
                    "direct_dependents": [],
                    "boundary_crossings": [],
                    "protected_overlap": [],
                    "file_touch_evidence": file_target["file_touch_evidence"],
                    "precision": "unknown",
                }
            )
            continue

        file_path = str(resolved_file_path)
        known_file = bool(file_target["known_file"])
        file_impact.append(
            {
                "file_path": file_path,
                "change_kind": str(file_target["change_kind"]),
                "known_file": known_file,
                "changed_ranges": file_target["changed_ranges"],
                "direct_dependencies": query_file_dependencies(root, Path(file_path))[
                    "depends_on"
                ]
                if known_file
                else [],
                "direct_dependents": _query_file_dependents(root, file_path)
                if known_file
                else [],
                "boundary_crossings": query_find_boundary_crossings_for_file(
                    root, Path(file_path)
                )["crossings"]
                if known_file
                else [],
                "protected_overlap": query_detect_protected_overlap_for_file(
                    root, Path(file_path)
                )["protected_targets"]
                if known_file
                else [],
                "file_touch_evidence": file_target["file_touch_evidence"],
                "precision": "file",
            }
        )

    symbol_impact.sort(key=lambda item: (item["file_path"], item["symbol_id"]))
    file_impact.sort(
        key=lambda item: (
            item["file_path"] is None,
            str(item["file_path"] or ""),
            str(item["change_kind"]),
        )
    )

    return {
        "patch_format": "unified_diff",
        "direct_targets": direct_targets,
        "symbol_impact": symbol_impact,
        "file_impact": file_impact,
    }
