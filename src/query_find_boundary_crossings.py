from __future__ import annotations

from pathlib import Path

from src.file_ownership_classifier import build_file_ownership_facts
from src.python_dependency_graph import build_python_dependency_graph
from src.query_symbol_metadata import query_symbol_metadata


def _module_name_for_file(file_path: Path) -> str:
    parts = list(file_path.with_suffix("").parts)

    if parts and parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)


def _top_level_package_for_file(file_path: Path) -> str:
    module_name = _module_name_for_file(file_path)
    if not module_name:
        return ""

    return module_name.split(".")[0]


def _ownership_map(root: Path) -> dict[str, str]:
    return {
        Path(str(fact["file_path"])).as_posix(): str(fact["ownership"])
        for fact in build_file_ownership_facts(root)
    }


def _module_to_file_map(dependency_graph: list[dict[str, object]]) -> dict[str, str]:
    module_to_file: dict[str, str] = {}

    for dependency in dependency_graph:
        file_path = Path(str(dependency["file_path"]))
        module_name = _module_name_for_file(file_path)
        if module_name:
            module_to_file[module_name] = file_path.as_posix()

    return module_to_file


def _build_crossing_records(
    source_file_path: str,
    related_file_path: str,
    relation_kind: str,
    ownership_by_file: dict[str, str],
) -> list[dict[str, str]]:
    source_path = Path(source_file_path)
    related_path = Path(related_file_path)
    crossings: list[dict[str, str]] = []

    if source_file_path != related_file_path:
        crossings.append(
            {
                "related_target": related_file_path,
                "relation_kind": relation_kind,
                "boundary_type": "file",
                "from_value": source_file_path,
                "to_value": related_file_path,
                "evidence_basis": "file_dependency_graph",
            }
        )

    source_top_level = _top_level_package_for_file(source_path)
    related_top_level = _top_level_package_for_file(related_path)
    if source_top_level and related_top_level and source_top_level != related_top_level:
        crossings.append(
            {
                "related_target": related_file_path,
                "relation_kind": relation_kind,
                "boundary_type": "top_level_package",
                "from_value": source_top_level,
                "to_value": related_top_level,
                "evidence_basis": "normalized_file_paths",
            }
        )

    source_ownership = ownership_by_file.get(source_file_path)
    related_ownership = ownership_by_file.get(related_file_path)
    if (
        source_ownership
        and related_ownership
        and source_ownership != "unknown"
        and related_ownership != "unknown"
        and source_ownership != related_ownership
    ):
        crossings.append(
            {
                "related_target": related_file_path,
                "relation_kind": relation_kind,
                "boundary_type": "ownership",
                "from_value": source_ownership,
                "to_value": related_ownership,
                "evidence_basis": "file_ownership_facts",
            }
        )

    return crossings


def query_find_boundary_crossings_for_file(root: Path, file_path: Path) -> dict[str, object]:
    relative_file_path = file_path

    if file_path.is_absolute():
        relative_file_path = file_path.relative_to(root)

    source_file_path = relative_file_path.as_posix()
    dependency_graph = build_python_dependency_graph(root)
    ownership_by_file = _ownership_map(root)
    module_to_file = _module_to_file_map(dependency_graph)
    source_module_name = _module_name_for_file(Path(source_file_path))
    outgoing_targets: list[str] = []
    incoming_targets: list[str] = []

    for dependency in dependency_graph:
        dependency_file_path = Path(str(dependency["file_path"])).as_posix()
        if dependency_file_path == source_file_path:
            outgoing_targets.extend(
                module_to_file[target]
                for target in dependency["depends_on"]
                if isinstance(target, str) and target in module_to_file
            )
        if source_module_name and source_module_name in dependency["depends_on"]:
            incoming_targets.append(dependency_file_path)

    crossings: list[dict[str, str]] = []

    for related_file_path in sorted(set(outgoing_targets)):
        crossings.extend(
            _build_crossing_records(
                source_file_path,
                related_file_path,
                "dependency",
                ownership_by_file,
            )
        )

    for related_file_path in sorted(set(incoming_targets)):
        crossings.extend(
            _build_crossing_records(
                source_file_path,
                related_file_path,
                "dependent",
                ownership_by_file,
            )
        )

    return {
        "file_path": source_file_path,
        "found": any(
            Path(str(dependency["file_path"])).as_posix() == source_file_path
            for dependency in dependency_graph
        ),
        "crossings": crossings,
    }


def query_find_boundary_crossings(root: Path, symbol_id: str) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "crossings": [],
        }

    metadata = metadata_result["metadata"]
    file_result = query_find_boundary_crossings_for_file(
        root, Path(str(metadata["file_path"]))
    )
    crossings: list[dict[str, str]] = []

    for crossing in file_result["crossings"]:
        crossings.append(
            {
                "source_symbol_id": symbol_id,
                "source_file_path": str(metadata["file_path"]),
                **crossing,
            }
        )

    return {
        "symbol_id": symbol_id,
        "found": True,
        "crossings": crossings,
    }
