import json
from pathlib import Path

from src.cli import main


def test_end_to_end_cli_workflow(tmp_path: Path, capsys) -> None:
    python_file = tmp_path / "sample.py"
    python_file.write_text(
        "import os\n\n"
        "def foo():\n"
        "    return os.getcwd()\n",
        encoding="utf-8",
    )

    assert main(["build", "--root", str(tmp_path)]) == 0
    build_payload = json.loads(capsys.readouterr().out)

    assert main(["build", "--root", str(tmp_path)]) == 0
    second_build_payload = json.loads(capsys.readouterr().out)

    assert build_payload == second_build_payload
    assert build_payload["contract_name"] == "DefiantCodeGraphFacts"
    assert build_payload["contract_version"] == "dcg.facts.v1"
    assert build_payload["graph_id"] == str(tmp_path)
    assert build_payload["meta"]["parser_family"] == "python-ast"
    assert build_payload["meta"]["snapshot_id"]
    assert build_payload["meta"]["notes"] == [
        "repo_file_facts=1",
        "dependency_facts=1",
        "ownership_facts=1",
        "symbol_relationship_facts=1",
        "snapshot_file_count=1",
    ]

    assert (
        main(
            [
                "query",
                "--root",
                str(tmp_path),
                "--type",
                "file_dependencies",
                "--file-path",
                "sample.py",
            ]
        )
        == 0
    )
    query_result = json.loads(capsys.readouterr().out)

    assert (
        main(
            [
                "query",
                "--root",
                str(tmp_path),
                "--type",
                "file_dependencies",
                "--file-path",
                "sample.py",
            ]
        )
        == 0
    )
    second_query_result = json.loads(capsys.readouterr().out)

    assert query_result == second_query_result
    assert query_result == {
        "file_path": "sample.py",
        "depends_on": ["os"],
    }
