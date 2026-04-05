from src.schema_validator import validate_facts_payload


def test_validate_facts_payload_with_minimal_valid_payload() -> None:
    payload = {
        "contract_name": "DefiantCodeGraphFacts",
        "contract_version": "dcg.facts.v1",
        "graph_id": "graph-1",
    }

    validate_facts_payload(payload)