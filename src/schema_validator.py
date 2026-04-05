from __future__ import annotations

import json
from typing import Any

from jsonschema import validate

from src.schema_utils import get_schema_path, verify_vendored_schema_checksum


def load_vendored_schema() -> dict[str, Any]:
    with get_schema_path().open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


def validate_facts_payload(payload: dict[str, Any]) -> None:
    verify_vendored_schema_checksum()
    validate(instance=payload, schema=load_vendored_schema())
