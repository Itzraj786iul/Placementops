import pytest

from app.platform.auth.password import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    password = "PlacementOS123!"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)
