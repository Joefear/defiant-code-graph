from __future__ import annotations

from pathlib import Path

from src.build_validated_dcg_payload import build_validated_dcg_payload


def build_dcg_facts(root: Path) -> dict[str, object]:
    return build_validated_dcg_payload(root)
