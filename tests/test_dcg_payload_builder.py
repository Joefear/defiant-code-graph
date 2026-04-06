from pathlib import Path

from src.build_validated_dcg_payload import build_validated_dcg_payload
from src.dcg_payload_builder import build_minimal_dcg_payload


def test_build_minimal_dcg_payload(tmp_path: Path) -> None:
    temp_file_b = tmp_path / "b.py"
    temp_file_a = tmp_path / "a.py"
    temp_file_b.write_text("import os\n\ndef beta():\n    pass\n", encoding="utf-8")
    temp_file_a.write_text("def alpha():\n    pass\n", encoding="utf-8")

    payload = build_minimal_dcg_payload(tmp_path)
    second_payload = build_minimal_dcg_payload(tmp_path)

    assert payload["contract_name"] == "DefiantCodeGraphFacts"
    assert payload["contract_version"] == "dcg.facts.v1"
    assert payload["graph_id"] == str(tmp_path)
    assert payload == second_payload
    assert payload["meta"]["parser_family"] == "python-ast"
    assert payload["meta"]["snapshot_id"]
    assert payload["meta"]["notes"] == [
        "repo_file_facts=2",
        "dependency_facts=2",
        "ownership_facts=2",
        "symbol_relationship_facts=2",
        "snapshot_file_count=2",
    ]
    assert "ownership_facts" not in payload
    assert "impact_facts" not in payload
    assert build_validated_dcg_payload(tmp_path) == payload
