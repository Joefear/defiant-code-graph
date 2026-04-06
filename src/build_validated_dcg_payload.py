from __future__ import annotations

from pathlib import Path

from src.dcg_contract_validator import validate_dcg_payload
from src.dcg_payload_builder import build_minimal_dcg_payload


def build_validated_dcg_payload(root: Path) -> dict[str, object]:
    payload = build_minimal_dcg_payload(root)
    validation_result = validate_dcg_payload(payload)

    if not validation_result["valid"]:
        errors = validation_result["errors"]
        raise ValueError(f"DCG payload validation failed: {errors}")

    return payload
