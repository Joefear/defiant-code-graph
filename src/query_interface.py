from __future__ import annotations

from pathlib import Path

from src.query_classify_change_type import query_classify_change_type
from src.query_determine_edit_strategy import query_determine_edit_strategy
from src.query_compare_intent_to_patch import query_compare_intent_to_patch
from src.query_analyze_patch_impact import query_analyze_patch_impact
from src.query_detect_protected_overlap import (
    query_detect_protected_overlap,
    query_detect_protected_overlap_for_file,
)
from src.query_analyze_patch_targets import query_analyze_patch_targets
from src.query_file_dependencies import query_file_dependencies
from src.query_find_boundary_crossings import (
    query_find_boundary_crossings,
    query_find_boundary_crossings_for_file,
)
from src.query_detect_generation_collision import query_detect_generation_collision
from src.query_file_outline import query_file_outline
from src.query_find_insertion_points import (
    query_find_insertion_points,
    query_find_insertion_points_for_file,
)
from src.query_related_symbols import query_related_symbols
from src.query_resolve_symbol import query_resolve_symbol
from src.query_symbol_metadata import query_symbol_metadata
from src.query_symbol_source import query_symbol_source


def run_query(root: Path, query_type: str, **kwargs: object) -> dict[str, object]:
    if query_type == "file_outline":
        return query_file_outline(root, kwargs["file_path"])
    if query_type == "file_dependencies":
        return query_file_dependencies(root, kwargs["file_path"])
    if query_type == "determine_edit_strategy":
        return query_determine_edit_strategy(
            root,
            file_path=kwargs.get("file_path"),
            symbol_id=kwargs.get("symbol_id"),
            proposed_start_line=kwargs["proposed_start_line"],
            proposed_end_line=kwargs["proposed_end_line"],
        )
    if query_type == "detect_generation_collision":
        return query_detect_generation_collision(
            root,
            file_path=kwargs.get("file_path"),
            symbol_id=kwargs.get("symbol_id"),
            proposed_start_line=kwargs["proposed_start_line"],
            proposed_end_line=kwargs["proposed_end_line"],
        )
    if query_type == "find_insertion_points":
        if "symbol_id" in kwargs:
            return query_find_insertion_points(root, symbol_id=kwargs["symbol_id"])
        return query_find_insertion_points_for_file(root, kwargs["file_path"])
    if query_type == "classify_change_type":
        return query_classify_change_type(root, kwargs["patch_text"])
    if query_type == "compare_intent_to_patch":
        return query_compare_intent_to_patch(root, kwargs["intent"], kwargs["patch_text"])
    if query_type == "analyze_patch_impact":
        return query_analyze_patch_impact(root, kwargs["patch_text"])
    if query_type == "analyze_patch_targets":
        return query_analyze_patch_targets(root, kwargs["patch_text"])
    if query_type == "detect_protected_overlap":
        if "symbol_id" in kwargs:
            return query_detect_protected_overlap(
                root,
                kwargs["symbol_id"],
                kwargs.get("span"),
            )
        return query_detect_protected_overlap_for_file(
            root,
            kwargs["file_path"],
            kwargs.get("span"),
        )
    if query_type == "find_boundary_crossings":
        if "symbol_id" in kwargs:
            return query_find_boundary_crossings(root, kwargs["symbol_id"])
        return query_find_boundary_crossings_for_file(root, kwargs["file_path"])
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


def run_determine_edit_strategy_query(
    root: Path,
    *,
    proposed_start_line: int,
    proposed_end_line: int,
    file_path: Path | None = None,
    symbol_id: str | None = None,
) -> dict[str, object]:
    return query_determine_edit_strategy(
        root,
        file_path=file_path,
        symbol_id=symbol_id,
        proposed_start_line=proposed_start_line,
        proposed_end_line=proposed_end_line,
    )


def run_detect_generation_collision_query(
    root: Path,
    *,
    proposed_start_line: int,
    proposed_end_line: int,
    file_path: Path | None = None,
    symbol_id: str | None = None,
) -> dict[str, object]:
    return query_detect_generation_collision(
        root,
        file_path=file_path,
        symbol_id=symbol_id,
        proposed_start_line=proposed_start_line,
        proposed_end_line=proposed_end_line,
    )


def run_find_insertion_points_query(
    root: Path, *, file_path: Path | None = None, symbol_id: str | None = None
) -> dict[str, object]:
    return query_find_insertion_points(root, file_path=file_path, symbol_id=symbol_id)


def run_classify_change_type_query(root: Path, patch_text: str) -> dict[str, object]:
    return query_classify_change_type(root, patch_text)


def run_compare_intent_to_patch_query(
    root: Path, intent: dict[str, object], patch_text: str
) -> dict[str, object]:
    return query_compare_intent_to_patch(root, intent, patch_text)


def run_analyze_patch_impact_query(root: Path, patch_text: str) -> dict[str, object]:
    return query_analyze_patch_impact(root, patch_text)


def run_analyze_patch_targets_query(root: Path, patch_text: str) -> dict[str, object]:
    return query_analyze_patch_targets(root, patch_text)


def run_detect_protected_overlap_query(
    root: Path,
    *,
    symbol_id: str | None = None,
    file_path: Path | None = None,
    span: dict[str, object] | None = None,
) -> dict[str, object]:
    if symbol_id is not None:
        return query_detect_protected_overlap(root, symbol_id, span)
    if file_path is not None:
        return query_detect_protected_overlap_for_file(root, file_path, span)

    raise ValueError("Either symbol_id or file_path is required")


def run_find_boundary_crossings_query(
    root: Path, *, symbol_id: str | None = None, file_path: Path | None = None
) -> dict[str, object]:
    if symbol_id is not None:
        return query_find_boundary_crossings(root, symbol_id)
    if file_path is not None:
        return query_find_boundary_crossings_for_file(root, file_path)

    raise ValueError("Either symbol_id or file_path is required")


def run_symbol_metadata_query(root: Path, symbol_id: str) -> dict[str, object]:
    return query_symbol_metadata(root, symbol_id)


def run_resolve_symbol_query(root: Path, symbol_name: str) -> dict[str, object]:
    return query_resolve_symbol(root, symbol_name)


def run_symbol_source_query(root: Path, symbol_id: str) -> dict[str, object]:
    return query_symbol_source(root, symbol_id)


def run_related_symbols_query(root: Path, symbol_id: str) -> dict[str, object]:
    return query_related_symbols(root, symbol_id)
