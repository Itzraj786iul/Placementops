from __future__ import annotations

from pydantic import BaseModel, Field


class MaintenancePublicStatus(BaseModel):
    enabled: bool
    title: str
    message: str
    estimated_completion: str | None = None
    support_contact: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None


class MaintenanceAdminResponse(MaintenancePublicStatus):
    allowed_roles: list[str] = Field(default_factory=list)
    updated_by: str | None = None


class MaintenanceUpdate(BaseModel):
    enabled: bool | None = None
    title: str | None = Field(default=None, min_length=1, max_length=200)
    message: str | None = Field(default=None, min_length=1, max_length=4000)
    estimated_completion: str | None = None
    support_contact: str | None = None
    starts_at: str | None = None
    ends_at: str | None = None
    allowed_roles: list[str] | None = None
    confirm: bool = False
