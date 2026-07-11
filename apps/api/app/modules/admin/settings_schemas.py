from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class SettingMeta(BaseModel):
    updated_at: datetime | None = None
    updated_by: UUID | None = None


class StorageHealth(BaseModel):
    configured: bool
    cloud_name: str | None = None
    status: str
    upload_limits_mb: dict[str, float]
    allowed_extensions: dict[str, list[str]]


class AuthIntegrationStatus(BaseModel):
    google_oauth_env_configured: bool
    env_allowed_email_domain: str
    access_token_expire_minutes: int


class NotificationIntegrationStatus(BaseModel):
    email_configured: bool
    email_provider: str
    email_from: str
    template_previews: list[str]


class SecurityStatus(BaseModel):
    password_policy: str
    rate_limit_status: str
    audit_logging_status: str
    environment_mode: str


class IntegrationsStatus(BaseModel):
    storage: StorageHealth
    authentication: AuthIntegrationStatus
    notifications: NotificationIntegrationStatus
    security: SecurityStatus


class AdminSettingsResponse(BaseModel):
    settings: dict[str, Any]
    meta: dict[str, SettingMeta] = Field(default_factory=dict)
    sections: dict[str, list[str]]
    sensitive_keys: list[str]
    integrations: IntegrationsStatus


class AdminSettingsUpdate(BaseModel):
    settings: dict[str, Any] = Field(min_length=1)
    confirm_sensitive: bool = False
