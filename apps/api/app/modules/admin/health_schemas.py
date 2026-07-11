from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

HealthLevel = Literal["healthy", "warning", "critical"]
ComponentStatus = Literal["healthy", "warning", "critical", "unknown", "skipped"]


class DatabaseHealth(BaseModel):
    status: ComponentStatus
    connected: bool
    response_time_ms: float | None = None
    migration_version: str | None = None
    active_connections: int | None = None
    detail: str | None = None


class StorageHealth(BaseModel):
    status: ComponentStatus
    provider: str = "cloudinary"
    configured: bool
    reachable: bool | None = None
    upload_test: str = "skipped"
    detail: str | None = None


class EmailHealth(BaseModel):
    status: ComponentStatus
    provider: str
    configured: bool
    reachable: bool | None = None
    last_send_status: str | None = None
    template_count: int
    detail: str | None = None


class AuthHealth(BaseModel):
    status: ComponentStatus
    google_oauth_configured: bool
    google_oauth_reachable: bool | None = None
    jwt_status: ComponentStatus
    session_store_status: ComponentStatus
    detail: str | None = None


class ApplicationInfo(BaseModel):
    status: ComponentStatus = "healthy"
    version: str
    environment: str
    build_date: str | None = None
    git_commit: str | None = None
    uptime_seconds: int


class SystemStatistics(BaseModel):
    users: int
    students: int
    conveners: int
    companies: int
    hiring_opportunities: int
    applications: int
    notifications: int
    storage_files_approx: int


class SystemHealthResponse(BaseModel):
    overall_status: HealthLevel
    checked_at: datetime
    cached: bool = False
    check_duration_ms: float
    database: DatabaseHealth
    storage: StorageHealth
    email: EmailHealth
    authentication: AuthHealth
    application: ApplicationInfo
    statistics: SystemStatistics
    notes: list[str] = Field(default_factory=list)
