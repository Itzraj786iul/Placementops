from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.modules.admin.access import ensure_super_admin
from app.modules.admin.exceptions import AdminValidationError
from app.modules.admin.maintenance_schemas import (
    MaintenanceAdminResponse,
    MaintenancePublicStatus,
    MaintenanceUpdate,
)
from app.modules.admin.maintenance_state import (
    get_maintenance_state,
    user_bypasses_maintenance,
)
from app.modules.admin.settings_cache import invalidate_settings_cache
from app.modules.admin.settings_catalog import validate_setting_value
from app.modules.admin.settings_repository import AdminSettingsRepository
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.users.models import User
from app.platform.permissions.permissions import has_role
from app.utils.datetime import utc_now

_KEY_MAP = {
    "enabled": "maintenance.enabled",
    "title": "maintenance.title",
    "message": "maintenance.message",
    "estimated_completion": "maintenance.estimated_completion",
    "support_contact": "maintenance.support_contact",
    "starts_at": "maintenance.starts_at",
    "ends_at": "maintenance.ends_at",
    "allowed_roles": "maintenance.allowed_roles",
}


class MaintenanceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminSettingsRepository(db)

    def get_public_status(self) -> MaintenancePublicStatus:
        state = get_maintenance_state()
        return MaintenancePublicStatus(**state.public_payload)

    def get_admin_status(self, actor: User) -> MaintenanceAdminResponse:
        ensure_super_admin(actor)
        state = get_maintenance_state()
        return MaintenanceAdminResponse(
            **state.public_payload,
            allowed_roles=list(state.allowed_roles),
            updated_by=state.updated_by,
        )

    def update(
        self,
        actor: User,
        payload: MaintenanceUpdate,
    ) -> MaintenanceAdminResponse:
        ensure_super_admin(actor)
        data = payload.model_dump(exclude_unset=True)
        data.pop("confirm", None)
        if not data:
            raise AdminValidationError("No maintenance fields provided")

        enabling = data.get("enabled") is True
        disabling = data.get("enabled") is False
        if (enabling or disabling or "message" in data or "title" in data) and not payload.confirm:
            raise AdminValidationError(
                "Maintenance changes require confirm=true",
            )

        current = get_maintenance_state()
        merged_values: dict[str, Any] = {
            "enabled": current.enabled,
            "title": current.title,
            "message": current.message,
            "estimated_completion": current.estimated_completion,
            "support_contact": current.support_contact,
            "starts_at": current.starts_at,
            "ends_at": current.ends_at,
            "allowed_roles": list(current.allowed_roles),
        }
        merged_values.update(data)

        validated: dict[str, Any] = {}
        for field, value in merged_values.items():
            key = _KEY_MAP[field]
            try:
                validated[key] = validate_setting_value(key, value)
            except ValueError as exc:
                raise AdminValidationError(f"{key}: {exc}") from exc

        validated["maintenance.updated_by"] = str(actor.id)

        # Load previous for audit diffs
        previous_map: dict[str, Any] = {
            "maintenance.enabled": current.enabled,
            "maintenance.title": current.title,
            "maintenance.message": current.message,
            "maintenance.estimated_completion": current.estimated_completion,
            "maintenance.support_contact": current.support_contact,
            "maintenance.starts_at": current.starts_at,
            "maintenance.ends_at": current.ends_at,
            "maintenance.allowed_roles": list(current.allowed_roles),
            "maintenance.updated_by": current.updated_by,
        }

        for key, new_value in validated.items():
            old_value = previous_map.get(key)
            if field_equal(old_value, new_value):
                continue
            row = self.repository.upsert(
                key=key,
                value=new_value,
                updated_by=actor.id,
            )
            row.updated_at = utc_now()
            record_audit(
                self.db,
                entity_type=AuditEntityType.SYSTEM_SETTING,
                entity_id=row.id,
                action=AuditAction.UPDATE,
                performed_by=actor.id,
                old_values={key: old_value},
                new_values={key: new_value},
                metadata={"setting_key": key, "domain": "maintenance"},
            )

        self.db.commit()
        invalidate_settings_cache()
        # Warm cache with updated values for middleware
        from app.modules.admin.maintenance_state import warm_settings_cache

        warm_settings_cache()
        return self.get_admin_status(actor)

    @staticmethod
    def assert_user_may_authenticate(user: User) -> None:
        state = get_maintenance_state()
        if not state.enabled:
            return
        role_names = {role.name for role in user.roles}
        if user_bypasses_maintenance(role_names, state):
            return
        from app.platform.auth.exceptions import AuthError

        raise AuthError(
            state.message or "PlacementOS is under maintenance",
            status_code=503,
        )


def field_equal(a: Any, b: Any) -> bool:
    if isinstance(a, list) and isinstance(b, list):
        return list(a) == list(b)
    if isinstance(a, tuple) and isinstance(b, list):
        return list(a) == b
    if isinstance(a, list) and isinstance(b, tuple):
        return a == list(b)
    return a == b


def role_names_for_user(user: User) -> set[str]:
    return {role.name for role in user.roles}


def user_is_super_admin(user: User) -> bool:
    return has_role(user, "SUPER_ADMIN")
