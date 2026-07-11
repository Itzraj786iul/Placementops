from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modules.admin.exceptions import AdminForbiddenError, AdminValidationError
from app.modules.admin.settings_cache import (
    get_cached_settings,
    invalidate_settings_cache,
    set_cached_settings,
)
from app.modules.admin.settings_catalog import (
    is_blocked_key,
    validate_setting_value,
)
from app.modules.admin.settings_schemas import AdminSettingsUpdate
from app.modules.admin.settings_service import AdminSettingsService


def _actor(*role_names: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        roles=[SimpleNamespace(name=r) for r in role_names],
    )


def test_blocked_secret_keys() -> None:
    assert is_blocked_key("jwt_secret_key")
    assert is_blocked_key("auth.google_client_secret")
    assert is_blocked_key("cloudinary.api_secret")
    assert is_blocked_key("database_url")
    assert not is_blocked_key("general.college_name")


def test_validate_known_and_unknown_settings() -> None:
    assert validate_setting_value("general.college_name", "  NIT  ") == "NIT"
    assert validate_setting_value("auth.session_timeout_minutes", 30) == 30
    assert validate_setting_value("custom.feature_flag", {"on": True}) == {"on": True}
    with pytest.raises(ValueError):
        validate_setting_value("auth.session_timeout_minutes", 2)


def test_settings_cache_roundtrip() -> None:
    invalidate_settings_cache()
    assert get_cached_settings() is None
    set_cached_settings({"a": 1})
    assert get_cached_settings() == {"a": 1}
    invalidate_settings_cache()
    assert get_cached_settings() is None


def test_get_settings_requires_super_admin() -> None:
    service = AdminSettingsService(MagicMock())
    with pytest.raises(AdminForbiddenError):
        service.get_settings(_actor("PLACEMENT_CELL"))


def test_update_rejects_secrets_and_requires_confirm() -> None:
    service = AdminSettingsService(MagicMock())
    service.repository = MagicMock()
    service._load_merged = MagicMock(return_value=({"auth.google_oauth_enabled": True}, {}))  # noqa: SLF001

    with pytest.raises(AdminValidationError, match="not allowed"):
        service.update_settings(
            _actor("SUPER_ADMIN"),
            AdminSettingsUpdate(settings={"jwt_secret_key": "x"}),
        )

    with pytest.raises(AdminValidationError, match="confirm_sensitive"):
        service.update_settings(
            _actor("SUPER_ADMIN"),
            AdminSettingsUpdate(
                settings={"auth.google_oauth_enabled": False},
                confirm_sensitive=False,
            ),
        )
