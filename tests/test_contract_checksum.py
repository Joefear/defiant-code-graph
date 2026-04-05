from src.schema_utils import verify_vendored_schema_checksum


def test_verify_vendored_schema_checksum_returns_non_empty_string() -> None:
    checksum = verify_vendored_schema_checksum()
    assert checksum
