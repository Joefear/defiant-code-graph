from pathlib import Path

import pytest

from src.build_dcg_facts import build_dcg_facts


def test_build_dcg_facts(tmp_path: Path, monkeypatch) -> None:
    observed_roots: list[Path] = []
    payload = {
        "contract_name": "DefiantCodeGraphFacts",
        "contract_version": "dcg.facts.v1",
        "graph_id": str(tmp_path),
        "meta": {
            "parser_family": "python-ast",
            "snapshot_id": "snapshot-1",
            "notes": [],
        },
    }

    def build_payload(root: Path) -> dict[str, object]:
        observed_roots.append(root)
        return payload

    monkeypatch.setattr("src.build_dcg_facts.build_validated_dcg_payload", build_payload)

    assert build_dcg_facts(tmp_path) == payload
    assert build_dcg_facts(tmp_path) == payload
    assert observed_roots == [tmp_path, tmp_path]

    monkeypatch.setattr("src.build_dcg_facts.build_validated_dcg_payload", build_payload)
    assert build_dcg_facts(tmp_path) == payload

    with pytest.raises(ValueError, match="DCG payload validation failed"):
        monkeypatch.setattr(
            "src.build_dcg_facts.build_validated_dcg_payload",
            lambda root: (_ for _ in ()).throw(
                ValueError("DCG payload validation failed: ['bad payload']")
            ),
        )
        build_dcg_facts(tmp_path)
