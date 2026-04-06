from __future__ import annotations

from pathlib import Path

from src.repo_facts_builder import build_python_repo_facts


def build_minimal_dcg_payload(root: Path) -> dict[str, object]:
    return {
        "contract_name": "DefiantCodeGraphFacts",
        "contract_version": "dcg.facts.v1",
        "graph_id": str(root),
        "meta": build_python_repo_facts(root),
    }
