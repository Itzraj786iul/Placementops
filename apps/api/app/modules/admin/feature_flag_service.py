from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.modules.admin.access import ensure_super_admin
from app.modules.admin.exceptions import AdminValidationError
from app.modules.admin.feature_flag_cache import (
    get_cached_flag_map,
    invalidate_feature_flag_cache,
    set_cached_flag_map,
)
from app.modules.admin.feature_flag_catalog import (
    CRITICAL_FLAGS,
    FLAG_DEFAULTS,
    humanize_key,
)
from app.modules.admin.feature_flag_models import FLAG_SCOPES, FeatureFlag
from app.modules.admin.feature_flag_repository import FeatureFlagRepository
from app.modules.admin.feature_flag_schemas import (
    FeatureFlagListResponse,
    FeatureFlagResponse,
    FeatureFlagUpdate,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.users.models import User
from app.utils.datetime import utc_now


class FeatureFlagService:
    """Operational feature flags with cached is_enabled lookups."""

    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = FeatureFlagRepository(db)

    def is_enabled(self, flag_key: str) -> bool:
        """Return whether a flag is enabled. Unknown keys default to True."""
        if flag_key in CRITICAL_FLAGS:
            return True

        cached = get_cached_flag_map()
        if cached is not None:
            if flag_key in cached:
                return cached[flag_key]
            default = FLAG_DEFAULTS.get(flag_key, {}).get("enabled", True)
            return bool(default)

        enabled_map = self._rebuild_cache()
        if flag_key in enabled_map:
            return enabled_map[flag_key]
        return bool(FLAG_DEFAULTS.get(flag_key, {}).get("enabled", True))

    def list_flags(
        self,
        actor: User,
        *,
        search: str | None = None,
    ) -> FeatureFlagListResponse:
        ensure_super_admin(actor)
        rows_by_key = {row.key: row for row in self.repository.list_all()}
        keys = sorted(set(FLAG_DEFAULTS) | set(rows_by_key))

        items: list[FeatureFlagResponse] = []
        for key in keys:
            row = rows_by_key.get(key)
            item = self._to_response(key, row)
            if search:
                q = search.strip().lower()
                hay = f"{item.key} {item.name} {item.description or ''}".lower()
                if q not in hay:
                    continue
            items.append(item)

        return FeatureFlagListResponse(
            items=items,
            total=len(items),
            critical_keys=sorted(CRITICAL_FLAGS),
        )

    def update_flag(
        self,
        actor: User,
        key: str,
        payload: FeatureFlagUpdate,
    ) -> FeatureFlagResponse:
        ensure_super_admin(actor)
        key = key.strip()
        if not key:
            raise AdminValidationError("Flag key is required")

        if not payload.confirm:
            raise AdminValidationError(
                "Changing a feature flag requires confirm=true",
            )

        existing = self.repository.get_by_key(key)
        defaults = FLAG_DEFAULTS.get(key, {})
        current_enabled = (
            existing.enabled
            if existing is not None
            else bool(defaults.get("enabled", True))
        )
        current_name = existing.name if existing else str(defaults.get("name") or humanize_key(key))
        current_description = (
            existing.description
            if existing is not None
            else defaults.get("description")
        )
        current_scope = existing.scope if existing else str(defaults.get("scope", "GLOBAL"))
        current_metadata = (
            existing.metadata_
            if existing is not None
            else (defaults.get("metadata") or {})
        )

        new_enabled = payload.enabled if payload.enabled is not None else current_enabled
        new_name = payload.name.strip() if payload.name is not None else current_name
        new_description = (
            payload.description
            if payload.description is not None
            else current_description
        )
        new_scope = payload.scope.strip().upper() if payload.scope is not None else current_scope
        new_metadata = (
            payload.metadata if payload.metadata is not None else current_metadata
        )

        if new_scope not in FLAG_SCOPES:
            raise AdminValidationError(
                f"Invalid scope. Allowed: {', '.join(sorted(FLAG_SCOPES))}",
            )

        if key in CRITICAL_FLAGS and new_enabled is False:
            raise AdminValidationError(
                f"Critical flag '{key}' cannot be disabled",
            )

        old_values = {
            "key": key,
            "enabled": current_enabled,
            "name": current_name,
            "scope": current_scope,
        }
        new_values = {
            "key": key,
            "enabled": new_enabled,
            "name": new_name,
            "scope": new_scope,
        }

        row = self.repository.upsert(
            key=key,
            name=new_name,
            description=new_description if isinstance(new_description, str) or new_description is None else str(new_description),
            enabled=new_enabled,
            scope=new_scope,
            metadata=new_metadata if isinstance(new_metadata, dict) else {},
            updated_by=actor.id,
        )
        row.updated_at = utc_now()

        record_audit(
            self.db,
            entity_type=AuditEntityType.FEATURE_FLAG,
            entity_id=row.id,
            action=AuditAction.UPDATE,
            performed_by=actor.id,
            old_values=old_values,
            new_values=new_values,
            metadata={"flag_key": key},
        )
        self.db.commit()
        invalidate_feature_flag_cache()
        return self._to_response(key, row)

    def _rebuild_cache(self) -> dict[str, bool]:
        enabled_map: dict[str, bool] = {
            key: bool(meta.get("enabled", True)) for key, meta in FLAG_DEFAULTS.items()
        }
        for row in self.repository.list_all():
            enabled_map[row.key] = bool(row.enabled)
        for key in CRITICAL_FLAGS:
            enabled_map[key] = True
        set_cached_flag_map(enabled_map)
        return enabled_map

    def _to_response(
        self,
        key: str,
        row: FeatureFlag | None,
    ) -> FeatureFlagResponse:
        defaults = FLAG_DEFAULTS.get(key, {})
        if row is None:
            return FeatureFlagResponse(
                id=None,
                key=key,
                name=str(defaults.get("name") or humanize_key(key)),
                description=defaults.get("description"),
                enabled=bool(defaults.get("enabled", True)),
                scope=str(defaults.get("scope", "GLOBAL")),
                metadata={},
                updated_by=None,
                updated_by_email=None,
                updated_at=None,
                critical=key in CRITICAL_FLAGS,
                persisted=False,
            )
        return FeatureFlagResponse(
            id=row.id,
            key=row.key,
            name=row.name,
            description=row.description,
            enabled=row.enabled if key not in CRITICAL_FLAGS else True,
            scope=row.scope,
            metadata=row.metadata_ if isinstance(row.metadata_, dict) else {},
            updated_by=row.updated_by,
            updated_by_email=self.repository.user_email(row.updated_by),
            updated_at=row.updated_at,
            critical=key in CRITICAL_FLAGS,
            persisted=True,
        )
