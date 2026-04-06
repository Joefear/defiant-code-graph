from __future__ import annotations

from pathlib import Path

from src.query_symbol_metadata import query_symbol_metadata


def query_symbol_source(root: Path, symbol_id: str) -> dict[str, object]:
    metadata_result = query_symbol_metadata(root, symbol_id)

    if not metadata_result["found"]:
        return {
            "symbol_id": symbol_id,
            "found": False,
            "source": None,
            "file_path": None,
            "span": None,
        }

    metadata = metadata_result["metadata"]
    file_path = root / str(metadata["file_path"])
    start_line = int(metadata["start_line"])
    end_line = int(metadata["end_line"])
    lines = file_path.read_text(encoding="utf-8").splitlines(keepends=True)

    return {
        "symbol_id": symbol_id,
        "found": True,
        "source": "".join(lines[start_line - 1 : end_line]),
        "file_path": metadata["file_path"],
        "span": {
            "start_line": start_line,
            "end_line": end_line,
        },
    }
