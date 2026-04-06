from __future__ import annotations

from pathlib import Path

from src.build_dcg_facts import build_dcg_facts
from src.query_interface import run_query


def build_structural_facts(root: Path) -> dict[str, object]:
    return build_dcg_facts(root)


def run_structural_query(
    root: Path, query_type: str, **kwargs: object
) -> dict[str, object]:
    return run_query(root, query_type, **kwargs)
