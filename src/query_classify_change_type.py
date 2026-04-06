from __future__ import annotations

import re
from pathlib import Path

from src.query_analyze_patch_impact import query_analyze_patch_impact
from src.query_analyze_patch_targets import query_analyze_patch_targets


_DIFF_GIT_RE = re.compile(r"^diff --git a/(.+) b/(.+)$")


def _normalize_diff_path(raw_path: str) -> str | None:
    if raw_path == "/dev/null":
        return None

    normalized = raw_path
    if normalized.startswith("a/") or normalized.startswith("b/"):
        normalized = normalized[2:]

    return Path(normalized).as_posix()


def _parse_patch_line_counts(patch_text: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current_entry: dict[str, object] | None = None
    in_hunk = False

    for line in patch_text.splitlines():
        diff_match = _DIFF_GIT_RE.match(line)
        if diff_match:
            current_entry = {
                "old_file_path": _normalize_diff_path(diff_match.group(1)),
                "new_file_path": _normalize_diff_path(diff_match.group(2)),
                "added_lines": 0,
                "deleted_lines": 0,
            }
            entries.append(current_entry)
            in_hunk = False
            continue

        if current_entry is None:
            continue

        if line.startswith("--- "):
            current_entry["old_file_path"] = _normalize_diff_path(line[4:].strip())
            in_hunk = False
            continue
        if line.startswith("+++ "):
            current_entry["new_file_path"] = _normalize_diff_path(line[4:].strip())
            in_hunk = False
            continue
        if line.startswith("@@ "):
            in_hunk = True
            continue
        if not in_hunk:
            continue

        if line.startswith("+") and not line.startswith("+++"):
            current_entry["added_lines"] = int(current_entry["added_lines"]) + 1
        elif line.startswith("-") and not line.startswith("---"):
            current_entry["deleted_lines"] = int(current_entry["deleted_lines"]) + 1

    return entries


def _entry_key(item: dict[str, object]) -> tuple[bool, str, str, str]:
    resolved_file_path = item["resolved_file_path"]
    return (
        resolved_file_path is None,
        str(resolved_file_path or ""),
        str(item["old_file_path"] or ""),
        str(item["new_file_path"] or ""),
    )


def _resolved_file_path(old_file_path: str | None, new_file_path: str | None) -> str | None:
    if new_file_path is not None:
        return new_file_path
    return old_file_path


def _classifications_for_file(
    file_target: dict[str, object], added_lines: int, deleted_lines: int, structural: bool
) -> list[str]:
    change_kind = str(file_target["change_kind"])
    classifications: list[str] = []

    if change_kind == "added" or (added_lines > 0 and deleted_lines == 0):
        classifications.append("additive")
    if change_kind == "deleted" or (deleted_lines > 0 and added_lines == 0):
        classifications.append("destructive")
    if change_kind in {"modified", "path_changed"} and added_lines > 0 and deleted_lines > 0:
        classifications.append("modifying")
    if structural:
        classifications.append("structural")

    return classifications


def query_classify_change_type(root: Path, patch_text: str) -> dict[str, object]:
    patch_targets = query_analyze_patch_targets(root, patch_text)
    patch_impact = query_analyze_patch_impact(root, patch_text)
    line_counts_by_key = {
        (
            _resolved_file_path(
                _normalize_diff_path(str(entry["old_file_path"]))
                if entry["old_file_path"] is not None
                else None,
                _normalize_diff_path(str(entry["new_file_path"]))
                if entry["new_file_path"] is not None
                else None,
            ),
            _normalize_diff_path(str(entry["old_file_path"])) if entry["old_file_path"] is not None else None,
            _normalize_diff_path(str(entry["new_file_path"])) if entry["new_file_path"] is not None else None,
        ): entry
        for entry in _parse_patch_line_counts(patch_text)
    }

    symbol_impact_by_file: dict[str, list[dict[str, object]]] = {}
    for symbol_impact in patch_impact["symbol_impact"]:
        symbol_impact_by_file.setdefault(str(symbol_impact["file_path"]), []).append(symbol_impact)

    file_impact_by_file: dict[str, dict[str, object]] = {}
    for file_impact in patch_impact["file_impact"]:
        if file_impact["file_path"] is not None:
            file_impact_by_file[str(file_impact["file_path"])] = file_impact

    per_file_classification: list[dict[str, object]] = []

    for file_target in patch_targets["file_targets"]:
        key = (
            str(file_target["resolved_file_path"]) if file_target["resolved_file_path"] is not None else None,
            str(file_target["old_file_path"]) if file_target["old_file_path"] is not None else None,
            str(file_target["new_file_path"]) if file_target["new_file_path"] is not None else None,
        )
        line_counts = line_counts_by_key.get(
            key,
            {"added_lines": 0, "deleted_lines": 0},
        )
        resolved_file_path = (
            str(file_target["resolved_file_path"])
            if file_target["resolved_file_path"] is not None
            else None
        )
        boundary_crossings = symbol_impact_by_file.get(resolved_file_path or "", [])
        file_boundary_crossings = file_impact_by_file.get(resolved_file_path or "", {})
        structural = (
            str(file_target["change_kind"]) == "path_changed"
            or len(patch_targets["file_targets"]) > 1
            or len(file_target["symbol_touches"]) > 1
            or any(item["boundary_crossings"] for item in boundary_crossings)
            or bool(file_boundary_crossings.get("boundary_crossings"))
        )
        classifications = _classifications_for_file(
            file_target,
            int(line_counts["added_lines"]),
            int(line_counts["deleted_lines"]),
            structural,
        )
        per_file_classification.append(
            {
                "file_path": resolved_file_path,
                "change_kind": str(file_target["change_kind"]),
                "classifications": classifications,
                "evidence_summary": {
                    "added_lines": int(line_counts["added_lines"]),
                    "deleted_lines": int(line_counts["deleted_lines"]),
                    "touched_symbol_count": len(file_target["symbol_touches"]),
                    "touched_file_count": len(patch_targets["file_targets"]),
                    "boundary_crossing_count": sum(
                        len(item["boundary_crossings"]) for item in boundary_crossings
                    )
                    + len(file_boundary_crossings.get("boundary_crossings", [])),
                },
            }
        )

    patch_classifications = sorted(
        {
            classification
            for file_result in per_file_classification
            for classification in file_result["classifications"]
        }
    )

    return {
        "patch_format": "unified_diff",
        "classifications": patch_classifications,
        "per_file_classification": per_file_classification,
        "evidence_summary": {
            "file_count": len(patch_targets["file_targets"]),
            "symbol_count": len(patch_impact["symbol_impact"]),
            "file_only_count": len(patch_impact["file_impact"]),
        },
    }
