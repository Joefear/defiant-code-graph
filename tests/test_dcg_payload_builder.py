from pathlib import Path

from src.dcg_payload_builder import build_minimal_dcg_payload


def test_build_minimal_dcg_payload(tmp_path: Path) -> None:
    temp_file = tmp_path / "sample.py"
    temp_file.write_text("def foo():\n    pass\n", encoding="utf-8")

    payload = build_minimal_dcg_payload(tmp_path)

    assert payload["contract_name"] == "DefiantCodeGraphFacts"
    assert payload["contract_version"] == "dcg.facts.v1"
    assert payload["graph_id"] == str(tmp_path)
