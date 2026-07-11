"""Unit tests for unified email/password authentication helpers."""

from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.platform.auth.exceptions import AuthError
from app.platform.auth.password import hash_password, verify_password
from app.platform.auth.password_policy import validate_password_strength
from app.platform.auth.service import AuthService, _GENERIC_LOGIN_ERROR
from app.utils.datetime import utc_now


def test_password_policy_accepts_strong_password() -> None:
    assert validate_password_strength("SecurePass1") == "SecurePass1"


def test_password_policy_rejects_short() -> None:
    with pytest.raises(AuthError):
        validate_password_strength("Ab1")


def test_password_policy_requires_letter_and_digit() -> None:
    with pytest.raises(AuthError):
        validate_password_strength("abcdefgh")
    with pytest.raises(AuthError):
        validate_password_strength("12345678")


def test_bcrypt_hash_roundtrip() -> None:
    hashed = hash_password("PlacementOS123!")
    assert hashed != "PlacementOS123!"
    assert verify_password("PlacementOS123!", hashed)
    assert not verify_password("wrong", hashed)


def _service_with_user(user: SimpleNamespace | None) -> AuthService:
    db = MagicMock()
    service = AuthService(db)
    service.user_service = MagicMock()
    service.user_service.validate_college_email.side_effect = (
        lambda email: email.strip().lower()
    )
    service.user_service.get_by_college_email.return_value = user
    service.auth_repository = MagicMock()
    return service


def test_password_login_generic_error_when_missing_user() -> None:
    service = _service_with_user(None)
    with pytest.raises(AuthError) as exc:
        service.authenticate_password_login("nobody@nitrr.ac.in", "Whatever1")
    assert exc.value.message == _GENERIC_LOGIN_ERROR
    assert exc.value.status_code == 401


def test_password_login_rejects_unverified_email() -> None:
    user = SimpleNamespace(
        id=uuid4(),
        password_hash=hash_password("SecurePass1"),
        email_verified=False,
        locked_until=None,
        failed_login_attempts=0,
    )
    service = _service_with_user(user)
    with pytest.raises(AuthError) as exc:
        service.authenticate_password_login("student@nitrr.ac.in", "SecurePass1")
    assert "verify" in exc.value.message.lower()


def test_password_login_success_clears_lockout() -> None:
    user = SimpleNamespace(
        id=uuid4(),
        password_hash=hash_password("SecurePass1"),
        email_verified=True,
        locked_until=None,
        failed_login_attempts=2,
        status="active",
    )
    service = _service_with_user(user)
    service.user_service.require_active_user.return_value = user
    service.user_service.update_last_login.return_value = user

    with patch(
        "app.modules.admin.maintenance_service.MaintenanceService.assert_user_may_authenticate"
    ), patch("app.platform.auth.service.record_audit"):
        result = service.authenticate_password_login(
            "student@nitrr.ac.in",
            "SecurePass1",
        )

    assert result is user
    assert user.failed_login_attempts == 0
    assert user.locked_until is None


def test_password_login_lockout_blocks() -> None:
    user = SimpleNamespace(
        id=uuid4(),
        password_hash=hash_password("SecurePass1"),
        email_verified=True,
        locked_until=utc_now() + timedelta(minutes=10),
        failed_login_attempts=0,
    )
    service = _service_with_user(user)
    with pytest.raises(AuthError) as exc:
        service.authenticate_password_login("student@nitrr.ac.in", "SecurePass1")
    assert exc.value.status_code == 423


def test_create_password_rejects_when_already_set() -> None:
    user = SimpleNamespace(
        id=uuid4(),
        password_hash=hash_password("OldPass12"),
    )
    service = AuthService(MagicMock())
    service.user_service = MagicMock()
    with pytest.raises(AuthError):
        service.create_password(user, "NewPass12", "NewPass12")  # type: ignore[arg-type]


def test_forgot_password_does_not_reveal_missing_email() -> None:
    service = _service_with_user(None)
    result = service.request_password_reset("missing@nitrr.ac.in")
    assert "If an account exists" in result.message or "reset" in result.message.lower()
