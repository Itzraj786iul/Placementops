from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class FeatureFlagResponse(BaseModel):
    id: UUID | None = None
    key: str
    name: str
    description: str | None = None
    enabled: bool
    scope: str
    metadata: dict[str, Any] | None = None
    updated_by: UUID | None = None
    updated_by_email: str | None = None
    updated_at: datetime | None = None
    critical: bool = False
    persisted: bool = True


class FeatureFlagListResponse(BaseModel):
    items: list[FeatureFlagResponse]
    total: int
    critical_keys: list[str]


class FeatureFlagUpdate(BaseModel):
    enabled: bool | None = None
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    scope: str | None = None
    metadata: dict[str, Any] | None = None
    confirm: bool = False
