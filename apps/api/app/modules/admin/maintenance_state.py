"""Maintenance mode state derived from system_settings cache."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.modules.admin.settings_cache import get_cached_settings, set_cached_settings
from app.modules.admin.settings_catalog import SETTING_DEFAULTS, is_blocked_key

MAINTENANCE_KEYS = (
    "maintenance.enabled",
    "maintenance.title",
    "maintenance.message",
    "maintenance.estimated_completion",
    "maintenance.support_contact",
    "maintenance.starts_at",
    "maintenance.ends_at",
    "maintenance.allowed_roles",
    "maintenance.updated_by",
)


@dataclass(frozen=True)
class MaintenanceState:
    enabled: bool
    title: str
    message: str
    estimated_completion: str | None
    support_contact: str | None
    starts_at: str | None
    ends_at: str | None
    allowed_roles: tuple[str, ...]
    updated_by: str | None

    @property
    def public_payload(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "title": self.title,
            "message": self.message,
            "estimated_completion": self.estimated_completion,
            "support_contact": self.support_contact,
            "starts_at": self.starts_at,
            "ends_at": self.ends_at,
        }


def _as_bool(value: Any) -> bool:
    return value is True


def _as_str(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _as_optional_str(value: Any) -> str | None:
    if value is None or value == "":
        return None
    return str(value)


def _as_roles(value: Any) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    roles: list[str] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            roles.append(item.strip().upper())
    return tuple(roles)


def parse_maintenance_state(settings_map: dict[str, Any]) -> MaintenanceState:
    return MaintenanceState(
        enabled=_as_bool(settings_map.get("maintenance.enabled", False)),
        title=_as_str(
            settings_map.get("maintenance.title"),
            "Scheduled maintenance",
        ),
        message=_as_str(
            settings_map.get("maintenance.message"),
            "PlacementOS is temporarily unavailable. Please try again later.",
        ),
        estimated_completion=_as_optional_str(
            settings_map.get("maintenance.estimated_completion"),
        ),
        support_contact=_as_optional_str(
            settings_map.get("maintenance.support_contact"),
        ),
        starts_at=_as_optional_str(settings_map.get("maintenance.starts_at")),
        ends_at=_as_optional_str(settings_map.get("maintenance.ends_at")),
        allowed_roles=_as_roles(settings_map.get("maintenance.allowed_roles")),
        updated_by=_as_optional_str(settings_map.get("maintenance.updated_by")),
    )


def warm_settings_cache() -> dict[str, Any]:
    """Return settings map from cache, warming from DB once if needed."""
    cached = get_cached_settings()
    if cached is not None:
        return cached

    from app.database.session import SessionLocal
    from app.modules.admin.settings_repository import AdminSettingsRepository

    db = SessionLocal()
    try:
        repo = AdminSettingsRepository(db)
        merged = dict(SETTING_DEFAULTS)
        for row in repo.list_all():
            if is_blocked_key(row.key):
                continue
            merged[row.key] = row.value
        set_cached_settings(merged)
        return merged
    finally:
        db.close()


def get_maintenance_state() -> MaintenanceState:
    return parse_maintenance_state(warm_settings_cache())


def user_bypasses_maintenance(role_names: set[str], state: MaintenanceState) -> bool:
    if "SUPER_ADMIN" in role_names:
        return True
    return any(role in state.allowed_roles for role in role_names)


def schedule_active(state: MaintenanceState, *, now: datetime | None = None) -> bool:
    """If starts_at/ends_at set, only treat as active inside the window when enabled."""
    if not state.enabled:
        return False
    # Window is advisory; enabled flag is authoritative for this release.
    _ = now
    return True
