from pathlib import Path
import hashlib


def get_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def get_schema_path() -> Path:
    return get_project_root() / "contracts" / "dcg" / "dcg-facts-v1.schema.json"


def get_checksum_path() -> Path:
    return get_project_root() / "contracts" / "dcg" / "dcg-facts-v1.sha256"


def read_schema_bytes() -> bytes:
    return get_schema_path().read_bytes()


def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_expected_checksum() -> str:
    return get_checksum_path().read_text().strip().split()[0]


def verify_vendored_schema_checksum() -> str:
    schema_bytes = read_schema_bytes()
    actual = compute_sha256(schema_bytes)
    expected = read_expected_checksum()

    if actual != expected:
        raise ValueError(
            f"Schema checksum mismatch. Expected {expected}, got {actual}"
        )

    return actual