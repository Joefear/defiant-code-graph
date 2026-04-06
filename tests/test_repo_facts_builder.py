from pathlib import Path

from src.repo_facts_builder import build_python_repo_facts


def test_build_python_repo_facts(tmp_path: Path) -> None:
    file_a = tmp_path / "file_a.py"
    file_b = tmp_path / "file_b.py"

    file_a.write_text("def foo():\n    pass\n", encoding="utf-8")
    file_b.write_text("import os\n\ndef bar():\n    pass\n", encoding="utf-8")

    facts = build_python_repo_facts(tmp_path)

    assert facts["repo_root"] == str(tmp_path)
    assert len(facts["files"]) == 2
    assert [file_facts["file_path"] for file_facts in facts["files"]] == [
        "file_a.py",
        "file_b.py",
    ]
    assert facts["files"][0]["symbols"]
    assert facts["files"][1]["symbols"]
    assert facts["files"][1]["imports"] == ["os"]
