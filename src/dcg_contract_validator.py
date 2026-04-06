from __future__ import annotations

import json
from typing import Any

from jsonschema import Draft202012Validator

from src.schema_utils import (
    compute_sha256,
    get_schema_path,
    read_expected_checksum,
)


def load_vendored_schema() -> dict[str, Any]:
    with get_schema_path().open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


def compute_vendored_schema_checksum() -> str:
    return compute_sha256(get_schema_path().read_bytes())


def validate_dcg_payload(payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []
    actual_checksum = compute_vendored_schema_checksum()
    expected_checksum = read_expected_checksum()

    if actual_checksum != expected_checksum:
        errors.append(
            f"Schema checksum mismatch. Expected {expected_checksum}, got {actual_checksum}"
        )
        return {"valid": False, "errors": errors}

    validator = Draft202012Validator(load_vendored_schema())
    validation_errors = sorted(
        validator.iter_errors(payload),
        key=lambda error: tuple(error.path),
    )

    for validation_error in validation_errors:
        errors.append(validation_error.message)

    return {"valid": not errors, "errors": errors}
