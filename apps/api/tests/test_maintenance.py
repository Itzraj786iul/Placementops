from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.modules.admin.exceptions import AdminForbiddenError, AdminValidationError
from app.modules.admin.maintenance_schemas import MaintenanceUpdate
from app.modules.admin.maintenance_service import MaintenanceService
from app.modules.admin.maintenance_state import (
    MaintenanceState,
    parse_maintenance_state,
    user_bypasses_maintenance,
)
from app.modules.admin.settings_cache import invalidate_settings_cache, set_cached_settings
from app.platform.auth.exceptions import AuthError


def _actor(*role_names: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        roles=[SimpleNamespace(name=r) for r in role_names],
    )


def test_parse_maintenance_defaults() -> None:
    state = parse_maintenance_state({})
    assert state.enabled is False
    assert "maintenance" in state.message.lower() or state.title


def test_super_admin_bypasses() -> None:
    state = MaintenanceState(
        enabled=True,
        title="Down",
        message="Down",
        estimated_completion=None,
        support_contact=None,
        starts_at=None,
        ends_at=None,
        allowed_roles=("PLACEMENT_CELL",),
        updated_by=None,
    )
    assert user_bypasses_maintenance({"SUPER_ADMIN"}, state) is True
    assert user_bypasses_maintenance({"PLACEMENT_CELL"}, state) is True
    assert user_bypasses_maintenance({"STUDENT"}, state) is False
    assert user_bypasses_maintenance({"PLACEMENT_CONVENER"}, state) is False


def test_assert_authenticate_blocks_students() -> None:
    invalidate_settings_cache()
    set_cached_settings(
        {
            "maintenance.enabled": True,
            "maintenance.title": "Maintenance",
            "maintenance.message": "Closed",
            "maintenance.allowed_roles": [],
        },
    )
    with pytest.raises(AuthError) as exc:
        MaintenanceService.assert_user_may_authenticate(_actor("STUDENT"))
    assert exc.value.status_code == 503

    MaintenanceService.assert_user_may_authenticate(_actor("SUPER_ADMIN"))
    invalidate_settings_cache()


def test_admin_update_requires_super_admin_and_confirm() -> None:
    service = MaintenanceService(MagicMock())
    with pytest.raises(AdminForbiddenError):
        service.get_admin_status(_actor("PLACEMENT_CELL"))

    with patch(
        "app.modules.admin.maintenance_service.get_maintenance_state",
    ) as mock_state:
        mock_state.return_value = parse_maintenance_state(
            {"maintenance.enabled": False},
        )
        with pytest.raises(AdminValidationError, match="confirm"):
            service.update(
                _actor("SUPER_ADMIN"),
                MaintenanceUpdate(enabled=True, confirm=False),
            )
