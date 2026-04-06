from __future__ import annotations

import hashlib
from pathlib import Path

from src.repo_scanner import scan_repository


def build_repo_snapshot(root: Path) -> dict[str, object]:
    file_paths = scan_repository(root)
    digest = hashlib.sha256()

    for file_path in file_paths:
        relative_file_path = file_path.relative_to(root).as_posix()
        digest.update(relative_file_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_path.read_bytes())
        digest.update(b"\0")

    return {
        "snapshot_id": digest.hexdigest(),
        "file_count": len(file_paths),
    }
