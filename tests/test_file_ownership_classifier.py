from pathlib import Path

from src.file_ownership_classifier import build_file_ownership_facts


def test_build_file_ownership_facts(tmp_path: Path) -> None:
    generated_file = tmp_path / "a.generated.py"
    manual_file = tmp_path / "b.py"

    generated_file.write_text("# @generated\n", encoding="utf-8")
    manual_file.write_text("def foo():\n    pass\n", encoding="utf-8")

    ownership_facts = build_file_ownership_facts(tmp_path)

    assert ownership_facts == [
        {"file_path": "a.generated.py", "ownership": "generated"},
        {"file_path": "b.py", "ownership": "manual"},
    ]
