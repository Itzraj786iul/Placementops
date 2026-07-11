from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modules.admin.exceptions import AdminForbiddenError, AdminValidationError
from app.modules.admin.feature_flag_cache import (
    get_cached_flag_map,
    invalidate_feature_flag_cache,
    set_cached_flag_map,
)
from app.modules.admin.feature_flag_catalog import CRITICAL_FLAGS
from app.modules.admin.feature_flag_schemas import FeatureFlagUpdate
from app.modules.admin.feature_flag_service import FeatureFlagService


def _actor(*role_names: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        roles=[SimpleNamespace(name=r) for r in role_names],
    )


def test_critical_flags_defined() -> None:
    assert "audit_logging" in CRITICAL_FLAGS
    assert "authentication" in CRITICAL_FLAGS


def test_flag_cache_roundtrip() -> None:
    invalidate_feature_flag_cache()
    assert get_cached_flag_map() is None
    set_cached_flag_map({"exports": False})
    assert get_cached_flag_map() == {"exports": False}
    invalidate_feature_flag_cache()


def test_is_enabled_uses_cache_and_defaults() -> None:
    invalidate_feature_flag_cache()
    set_cached_flag_map({"exports": False, "notifications": True})
    service = FeatureFlagService(MagicMock())
    assert service.is_enabled("exports") is False
    assert service.is_enabled("notifications") is True
    assert service.is_enabled("unknown_custom_flag") is True
    assert service.is_enabled("audit_logging") is True
    invalidate_feature_flag_cache()


def test_list_requires_super_admin() -> None:
    service = FeatureFlagService(MagicMock())
    with pytest.raises(AdminForbiddenError):
        service.list_flags(_actor("PLACEMENT_CELL"))


def test_update_requires_confirm_and_blocks_critical_disable() -> None:
    db = MagicMock()
    service = FeatureFlagService(db)
    service.repository = MagicMock()
    service.repository.get_by_key.return_value = None

    with pytest.raises(AdminValidationError, match="confirm"):
        service.update_flag(
            _actor("SUPER_ADMIN"),
            "exports",
            FeatureFlagUpdate(enabled=False, confirm=False),
        )

    with pytest.raises(AdminValidationError, match="cannot be disabled"):
        service.update_flag(
            _actor("SUPER_ADMIN"),
            "audit_logging",
            FeatureFlagUpdate(enabled=False, confirm=True),
        )
