import pytest
from openhealthkit.utils.security import hash_password, verify_password


def test_pbkdf2_fallback_verification():
    # Test PBKDF2 format fallback string verification
    pbkdf2_hash = "pbkdf2:sha256:600000$0123456789abcdef0123456789abcdef$0123456789abcdef0123456789abcdef"
    assert verify_password("wrong_pass", pbkdf2_hash) is False

    # Invalid hash formats
    assert verify_password("pass", "invalid_hash_string") is False
    assert verify_password("pass", "pbkdf2:sha256:invalid") is False
