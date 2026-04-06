from pathlib import Path

import pytest

from src.build_validated_dcg_payload import build_validated_dcg_payload


def test_build_validated_dcg_payload(tmp_path: Path, monkeypatch) -> None:
    observed_payloads: list[dict[str, object]] = []
    valid_payload = {
        "contract_name": "DefiantCodeGraphFacts",
        "contract_version": "dcg.facts.v1",
        "graph_id": str(tmp_path),
    }

    monkeypatch.setattr(
        "src.build_validated_dcg_payload.build_minimal_dcg_payload",
        lambda root: valid_payload,
    )

    def validate_valid_payload(payload: dict[str, object]) -> dict[str, object]:
        observed_payloads.append(payload)
        return {"valid": True, "errors": []}

    monkeypatch.setattr(
        "src.build_validated_dcg_payload.validate_dcg_payload",
        validate_valid_payload,
    )

    assert build_validated_dcg_payload(tmp_path) == valid_payload
    assert observed_payloads == [valid_payload]

    def validate_invalid_payload(payload: dict[str, object]) -> dict[str, object]:
        observed_payloads.append(payload)
        return {"valid": False, "errors": ["bad payload"]}

    monkeypatch.setattr(
        "src.build_validated_dcg_payload.validate_dcg_payload",
        validate_invalid_payload,
    )

    with pytest.raises(ValueError, match="DCG payload validation failed"):
        build_validated_dcg_payload(tmp_path)

    assert observed_payloads == [valid_payload, valid_payload]
