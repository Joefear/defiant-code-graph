from __future__ import annotations

from pathlib import Path


EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".venv",
    "node_modules",
}


def _is_excluded(path: Path, root: Path) -> bool:
    relative_parts = path.relative_to(root).parts
    return any(part in EXCLUDED_DIRECTORY_NAMES for part in relative_parts)


def scan_repository(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and not _is_excluded(path, root)
    )
