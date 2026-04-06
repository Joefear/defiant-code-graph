import json
from pathlib import Path

from src.cli import main


def test_cli(tmp_path: Path, monkeypatch, capsys) -> None:
    build_result = {
        "contract_name": "DefiantCodeGraphFacts",
        "contract_version": "dcg.facts.v1",
        "graph_id": str(tmp_path),
        "meta": {
            "parser_family": "python-ast",
            "snapshot_id": "snapshot-1",
            "notes": [],
        },
    }
    query_result = {"query": "foo", "matches": []}
    observed_queries: list[tuple[Path, str, dict[str, object]]] = []

    monkeypatch.setattr("src.cli.build_dcg_facts", lambda root: build_result)

    def run_query(root: Path, query_type: str, **kwargs: object) -> dict[str, object]:
        observed_queries.append((root, query_type, kwargs))
        if query_type == "unknown":
            raise ValueError("Unknown query type: unknown")
        return query_result

    monkeypatch.setattr("src.cli.run_query", run_query)

    assert main(["build", "--root", str(tmp_path)]) == 0
    assert json.loads(capsys.readouterr().out) == build_result

    assert (
        main(
            [
                "query",
                "--root",
                str(tmp_path),
                "--type",
                "resolve_symbol",
                "--symbol-name",
                "foo",
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out) == query_result
    assert observed_queries == [(tmp_path, "resolve_symbol", {"symbol_name": "foo"})]

    assert main(["query", "--root", str(tmp_path), "--type", "unknown"]) == 1
    assert json.loads(capsys.readouterr().out) == {
        "error": "Unknown query type: unknown"
    }

    assert main(["unknown"]) == 1
    assert "error" in json.loads(capsys.readouterr().out)
