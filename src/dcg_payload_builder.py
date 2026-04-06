from __future__ import annotations

from pathlib import Path

from src.repo_facts_builder import build_python_repo_facts


def build_minimal_dcg_payload(root: Path) -> dict[str, object]:
    repo_facts = build_python_repo_facts(root)
    snapshot = repo_facts["snapshot"]

    return {
        "contract_name": "DefiantCodeGraphFacts",
        "contract_version": "dcg.facts.v1",
        "graph_id": str(root),
        "meta": {
            "parser_family": "python-ast",
            "snapshot_id": snapshot["snapshot_id"],
            "notes": [
                f"repo_file_facts={len(repo_facts['files'])}",
                f"dependency_facts={len(repo_facts['dependencies'])}",
                f"ownership_facts={len(repo_facts['ownership'])}",
                f"symbol_relationship_facts={len(repo_facts['symbol_relationships'])}",
                f"snapshot_file_count={snapshot['file_count']}",
            ],
        },
    }
