from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.admin.access import ensure_super_admin
from app.modules.admin.exceptions import AdminValidationError
from app.modules.admin.settings_cache import (
    get_cached_settings,
    invalidate_settings_cache,
    set_cached_settings,
)
from app.modules.admin.settings_catalog import (
    SECTION_KEYS,
    SENSITIVE_KEYS,
    SETTING_DEFAULTS,
    is_blocked_key,
    validate_setting_value,
)
from app.modules.admin.settings_repository import AdminSettingsRepository
from app.modules.admin.settings_schemas import (
    AdminSettingsResponse,
    AdminSettingsUpdate,
    AuthIntegrationStatus,
    IntegrationsStatus,
    NotificationIntegrationStatus,
    SecurityStatus,
    SettingMeta,
    StorageHealth,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.users.models import User
from app.platform.notifications.template_service import TemplateService
from app.platform.storage.types import ALLOWED_EXTENSIONS, CATEGORY_MAX_BYTES
from app.utils.datetime import utc_now


def _google_oauth_env_configured() -> bool:
    client_id = settings.GOOGLE_CLIENT_ID.strip()
    client_secret = settings.GOOGLE_CLIENT_SECRET.strip()
    if not client_id or not client_secret:
        return False
    if "****" in client_id or "****" in client_secret:
        return False
    if "your-" in client_id.lower() or "your-" in client_secret.lower():
        return False
    if len(client_secret) < 16:
        return False
    return True


def _environment_mode() -> str:
    return settings.ENVIRONMENT


class AdminSettingsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminSettingsRepository(db)

    def get_settings(self, actor: User) -> AdminSettingsResponse:
        ensure_super_admin(actor)
        merged, meta = self._load_merged()
        return AdminSettingsResponse(
            settings=merged,
            meta=meta,
            sections=SECTION_KEYS,
            sensitive_keys=sorted(SENSITIVE_KEYS),
            integrations=self._integrations(),
        )

    def update_settings(
        self,
        actor: User,
        payload: AdminSettingsUpdate,
    ) -> AdminSettingsResponse:
        ensure_super_admin(actor)
        if not payload.settings:
            raise AdminValidationError("No settings provided")

        for key in payload.settings:
            if is_blocked_key(key):
                raise AdminValidationError(
                    f"Setting key '{key}' is not allowed (secrets stay in environment)",
                )

        sensitive_touched = [
            key for key in payload.settings if key in SENSITIVE_KEYS
        ]
        if sensitive_touched and not payload.confirm_sensitive:
            raise AdminValidationError(
                "Sensitive setting changes require confirm_sensitive=true "
                f"({', '.join(sorted(sensitive_touched))})",
            )

        current, _ = self._load_merged(use_cache=False)
        validated: dict[str, Any] = {}
        for key, raw in payload.settings.items():
            try:
                validated[key] = validate_setting_value(key, raw)
            except ValueError as exc:
                raise AdminValidationError(f"{key}: {exc}") from exc

        for key, new_value in validated.items():
            old_value = current.get(key)
            if old_value == new_value:
                continue
            row = self.repository.upsert(
                key=key,
                value=new_value,
                updated_by=actor.id,
            )
            # Ensure updated_at refreshes even when SQLAlchemy misses JSON mutation
            row.updated_at = utc_now()
            record_audit(
                self.db,
                entity_type=AuditEntityType.SYSTEM_SETTING,
                entity_id=row.id,
                action=AuditAction.UPDATE,
                performed_by=actor.id,
                old_values={key: old_value},
                new_values={key: new_value},
                metadata={"setting_key": key},
            )

        self.db.commit()
        invalidate_settings_cache()
        return self.get_settings(actor)

    def _load_merged(
        self,
        *,
        use_cache: bool = True,
    ) -> tuple[dict[str, Any], dict[str, SettingMeta]]:
        if use_cache:
            cached = get_cached_settings()
            if cached is not None:
                # Meta is not cached separately; reload lightly for response accuracy
                rows = self.repository.list_all()
                meta = {
                    row.key: SettingMeta(
                        updated_at=row.updated_at,
                        updated_by=row.updated_by,
                    )
                    for row in rows
                }
                return dict(cached), meta

        merged = dict(SETTING_DEFAULTS)
        meta: dict[str, SettingMeta] = {}
        for row in self.repository.list_all():
            if is_blocked_key(row.key):
                continue
            merged[row.key] = row.value
            meta[row.key] = SettingMeta(
                updated_at=row.updated_at,
                updated_by=row.updated_by,
            )
        set_cached_settings(merged)
        return merged, meta

    def _integrations(self) -> IntegrationsStatus:
        templates = TemplateService()
        template_names = [t.value for t in templates.available_templates()]
        return IntegrationsStatus(
            storage=StorageHealth(
                configured=settings.cloudinary_configured,
                cloud_name=(
                    settings.CLOUDINARY_CLOUD_NAME.strip() or None
                    if settings.cloudinary_configured
                    else None
                ),
                status="healthy" if settings.cloudinary_configured else "not_configured",
                upload_limits_mb={
                    category.value.lower(): round(bytes_ / (1024 * 1024), 1)
                    for category, bytes_ in CATEGORY_MAX_BYTES.items()
                },
                allowed_extensions={
                    ext: sorted(mimes)
                    for ext, mimes in ALLOWED_EXTENSIONS.items()
                },
            ),
            authentication=AuthIntegrationStatus(
                google_oauth_env_configured=_google_oauth_env_configured(),
                env_allowed_email_domain=settings.ALLOWED_EMAIL_DOMAIN,
                access_token_expire_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            ),
            notifications=NotificationIntegrationStatus(
                email_configured=settings.email_configured,
                email_provider=settings.EMAIL_PROVIDER,
                email_from=settings.EMAIL_FROM,
                template_previews=template_names,
            ),
            security=SecurityStatus(
                password_policy="Future — managed via identity provider",
                rate_limit_status="Not configured (platform default)",
                audit_logging_status="Enabled",
                environment_mode=_environment_mode(),
            ),
        )
