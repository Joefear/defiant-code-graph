from __future__ import annotations

import re
from pathlib import Path

from src.code_graph_builder import build_python_symbol_index
from src.repo_scanner import scan_repository


_DIFF_GIT_RE = re.compile(r"^diff --git a/(.+) b/(.+)$")
_HUNK_RE = re.compile(
    r"^@@ -(?P<old_start>\d+)(?:,(?P<old_count>\d+))? \+(?P<new_start>\d+)(?:,(?P<new_count>\d+))? @@"
)


def _normalize_diff_path(raw_path: str) -> str | None:
    if raw_path == "/dev/null":
        return None

    normalized = raw_path
    if normalized.startswith("a/") or normalized.startswith("b/"):
        normalized = normalized[2:]

    return Path(normalized).as_posix()


def _parse_unified_diff(patch_text: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    current_entry: dict[str, object] | None = None

    for line in patch_text.splitlines():
        diff_match = _DIFF_GIT_RE.match(line)
        if diff_match:
            current_entry = {
                "old_file_path": _normalize_diff_path(diff_match.group(1)),
                "new_file_path": _normalize_diff_path(diff_match.group(2)),
                "hunks": [],
            }
            entries.append(current_entry)
            continue

        if current_entry is None:
            continue

        if line.startswith("--- "):
            current_entry["old_file_path"] = _normalize_diff_path(line[4:].strip())
            continue
        if line.startswith("+++ "):
            current_entry["new_file_path"] = _normalize_diff_path(line[4:].strip())
            continue

        hunk_match = _HUNK_RE.match(line)
        if hunk_match:
            current_entry["hunks"].append(
                {
                    "old_start": int(hunk_match.group("old_start")),
                    "old_count": int(hunk_match.group("old_count") or "1"),
                    "new_start": int(hunk_match.group("new_start")),
                    "new_count": int(hunk_match.group("new_count") or "1"),
                }
            )

    return entries


def _range_overlaps(
    range_start: int, range_count: int, symbol_start: int, symbol_end: int
) -> bool:
    if range_count <= 0:
        return False

    range_end = range_start + range_count - 1
    return not (range_end < symbol_start or range_start > symbol_end)


def _known_repo_files(root: Path) -> set[str]:
    return {file_path.relative_to(root).as_posix() for file_path in scan_repository(root)}


def _symbol_index_by_file(root: Path) -> dict[str, list[dict[str, object]]]:
    symbol_index: dict[str, list[dict[str, object]]] = {}

    for symbol in build_python_symbol_index(root):
        file_path = str(symbol["file_path"])
        symbol_index.setdefault(file_path, []).append(symbol)

    for symbols in symbol_index.values():
        symbols.sort(key=lambda item: (int(item["start_line"]), str(item["symbol_id"])))

    return symbol_index


def _change_kind(old_file_path: str | None, new_file_path: str | None) -> str:
    if old_file_path is None:
        return "added"
    if new_file_path is None:
        return "deleted"
    if old_file_path == new_file_path:
        return "modified"
    return "path_changed"


def _resolved_file_path(old_file_path: str | None, new_file_path: str | None) -> str | None:
    if new_file_path is not None:
        return new_file_path
    return old_file_path


def query_analyze_patch_targets(root: Path, patch_text: str) -> dict[str, object]:
    known_files = _known_repo_files(root)
    symbols_by_file = _symbol_index_by_file(root)
    file_results: list[dict[str, object]] = []

    for entry in _parse_unified_diff(patch_text):
        old_file_path = entry["old_file_path"]
        new_file_path = entry["new_file_path"]
        change_kind = _change_kind(old_file_path, new_file_path)
        resolved_file_path = _resolved_file_path(old_file_path, new_file_path)
        known_file = resolved_file_path in known_files if resolved_file_path is not None else False
        changed_ranges = [
            {
                "old_start": hunk["old_start"],
                "old_count": hunk["old_count"],
                "new_start": hunk["new_start"],
                "new_count": hunk["new_count"],
            }
            for hunk in entry["hunks"]
        ]

        symbol_touches: list[dict[str, object]] = []
        symbols = symbols_by_file.get(resolved_file_path or "", [])

        for symbol in symbols:
            overlaps = False
            for hunk in changed_ranges:
                if (
                    new_file_path == resolved_file_path
                    and _range_overlaps(
                        int(hunk["new_start"]),
                        int(hunk["new_count"]),
                        int(symbol["start_line"]),
                        int(symbol["end_line"]),
                    )
                ):
                    overlaps = True
                    break
                if (
                    old_file_path == resolved_file_path
                    and _range_overlaps(
                        int(hunk["old_start"]),
                        int(hunk["old_count"]),
                        int(symbol["start_line"]),
                        int(symbol["end_line"]),
                    )
                ):
                    overlaps = True
                    break

            if overlaps:
                symbol_touches.append(
                    {
                        "symbol_id": str(symbol["symbol_id"]),
                        "symbol_name": str(symbol["symbol_name"]),
                        "symbol_kind": str(symbol["symbol_kind"]),
                        "span": {
                            "start_line": int(symbol["start_line"]),
                            "end_line": int(symbol["end_line"]),
                        },
                        "evidence_basis": "patch_hunk_line_overlap",
                        "precision": "symbol",
                    }
                )

        file_touch_evidence: dict[str, object] | None = None
        if not symbol_touches:
            file_touch_evidence = {
                "file_path": resolved_file_path,
                "evidence_basis": "unified_diff_hunks",
                "precision": "file" if resolved_file_path is not None else "unknown",
            }

        file_results.append(
            {
                "resolved_file_path": resolved_file_path,
                "old_file_path": old_file_path,
                "new_file_path": new_file_path,
                "change_kind": change_kind,
                "known_file": known_file,
                "changed_ranges": changed_ranges,
                "symbol_touches": symbol_touches,
                "file_touch_evidence": file_touch_evidence,
            }
        )

    file_results.sort(
        key=lambda item: (
            item["resolved_file_path"] is None,
            str(item["resolved_file_path"] or ""),
            str(item["old_file_path"] or ""),
            str(item["new_file_path"] or ""),
        )
    )

    return {
        "patch_format": "unified_diff",
        "file_targets": file_results,
    }
