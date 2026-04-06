from pathlib import Path

from src.dcg_contract_validator import validate_dcg_payload
from src.schema_utils import compute_sha256


def test_validate_dcg_payload(tmp_path: Path, monkeypatch) -> None:
    schema_path = tmp_path / "dcg-facts-v1.schema.json"
    checksum_path = tmp_path / "dcg-facts-v1.sha256"

    schema_text = (
        "{\n"
        '  "$schema": "https://json-schema.org/draft/2020-12/schema",\n'
        '  "type": "object",\n'
        '  "additionalProperties": false,\n'
        '  "required": ["contract_name", "contract_version", "graph_id"],\n'
        '  "properties": {\n'
        '    "contract_name": {"type": "string", "const": "DefiantCodeGraphFacts"},\n'
        '    "contract_version": {"type": "string", "const": "dcg.facts.v1"},\n'
        '    "graph_id": {"type": "string", "minLength": 1}\n'
        "  }\n"
        "}\n"
    )
    schema_path.write_text(schema_text, encoding="utf-8")
    schema_checksum = compute_sha256(schema_path.read_bytes())

    monkeypatch.setattr("src.dcg_contract_validator.get_schema_path", lambda: schema_path)
    monkeypatch.setattr(
        "src.dcg_contract_validator.read_expected_checksum",
        lambda: checksum_path.read_text(encoding="utf-8").strip().split()[0],
    )

    checksum_path.write_text(
        f"{schema_checksum}  dcg-facts-v1.schema.json\n",
        encoding="utf-8",
    )
    assert validate_dcg_payload(
        {
            "contract_name": "DefiantCodeGraphFacts",
            "contract_version": "dcg.facts.v1",
            "graph_id": "graph-1",
        }
    ) == {"valid": True, "errors": []}

    checksum_path.write_text(
        "0000000000000000000000000000000000000000000000000000000000000000  dcg-facts-v1.schema.json\n",
        encoding="utf-8",
    )
    checksum_mismatch_result = validate_dcg_payload(
        {
            "contract_name": "DefiantCodeGraphFacts",
            "contract_version": "dcg.facts.v1",
            "graph_id": "graph-1",
        }
    )
    assert checksum_mismatch_result["valid"] is False
    assert checksum_mismatch_result["errors"]

    checksum_path.write_text(
        f"{schema_checksum}  dcg-facts-v1.schema.json\n",
        encoding="utf-8",
    )
    malformed_payload_result = validate_dcg_payload(
        {
            "contract_name": "DefiantCodeGraphFacts",
            "contract_version": "dcg.facts.v1",
        }
    )
    assert malformed_payload_result["valid"] is False
    assert malformed_payload_result["errors"]

    no_coercion_result = validate_dcg_payload(
        {
            "contract_name": "DefiantCodeGraphFacts",
            "contract_version": "dcg.facts.v1",
            "graph_id": 1,
        }
    )
    assert no_coercion_result["valid"] is False
    assert no_coercion_result["errors"]
