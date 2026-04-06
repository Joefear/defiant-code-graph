from __future__ import annotations

from pathlib import Path


def normalize_symbols(
    file_path: Path, raw_symbols: list[dict[str, object]]
) -> list[dict[str, object]]:
    normalized_symbols: list[dict[str, object]] = []

    for raw_symbol in raw_symbols:
        symbol_name = raw_symbol["symbol_name"]
        start_line = raw_symbol["start_line"]

        normalized_symbols.append(
            {
                "symbol_id": f"{file_path.as_posix()}:{symbol_name}:{start_line}",
                "symbol_name": symbol_name,
                "symbol_kind": raw_symbol["symbol_kind"],
                "file_path": file_path.as_posix(),
                "start_line": start_line,
                "end_line": raw_symbol["end_line"],
            }
        )

    return normalized_symbols
