from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.modules.admin.exceptions import AdminForbiddenError
from app.modules.admin.health_cache import (
    get_cached_health,
    invalidate_health_cache,
    set_cached_health,
)
from app.modules.admin.health_schemas import SystemHealthResponse
from app.modules.admin.health_service import (
    AdminHealthService,
    _jwt_status,
    _worst,
)


def _actor(*role_names: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        roles=[SimpleNamespace(name=r) for r in role_names],
    )


def test_worst_status() -> None:
    assert _worst("healthy", "healthy") == "healthy"
    assert _worst("healthy", "warning") == "warning"
    assert _worst("warning", "critical") == "critical"


def test_jwt_status_warns_on_default_secret() -> None:
    with patch("app.modules.admin.health_service.settings") as mock_settings:
        mock_settings.JWT_SECRET_KEY = (
            "change-me-in-production-use-a-long-random-secret"
        )
        assert _jwt_status() == "warning"
        mock_settings.JWT_SECRET_KEY = "x" * 48
        assert _jwt_status() == "healthy"


def test_health_cache_ttl_helpers() -> None:
    invalidate_health_cache()
    assert get_cached_health() is None
    set_cached_health({"overall_status": "healthy"})
    assert get_cached_health() == {"overall_status": "healthy"}
    invalidate_health_cache()
    assert get_cached_health() is None


def test_system_health_requires_super_admin() -> None:
    service = AdminHealthService(MagicMock())
    with pytest.raises(AdminForbiddenError):
        service.get_system_health(_actor("PLACEMENT_CELL"))


def test_system_health_uses_cache() -> None:
    invalidate_health_cache()
    service = AdminHealthService(MagicMock())
    fake = SystemHealthResponse.model_validate(
        {
            "overall_status": "healthy",
            "checked_at": "2026-07-11T00:00:00Z",
            "cached": False,
            "check_duration_ms": 12.5,
            "database": {
                "status": "healthy",
                "connected": True,
                "response_time_ms": 1.2,
                "migration_version": "013_system_settings",
                "active_connections": 3,
            },
            "storage": {
                "status": "healthy",
                "configured": True,
                "reachable": True,
                "upload_test": "skipped",
            },
            "email": {
                "status": "healthy",
                "provider": "resend",
                "configured": True,
                "reachable": True,
                "last_send_status": "none",
                "template_count": 4,
            },
            "authentication": {
                "status": "healthy",
                "google_oauth_configured": True,
                "google_oauth_reachable": True,
                "jwt_status": "healthy",
                "session_store_status": "healthy",
            },
            "application": {
                "status": "healthy",
                "version": "0.1.0",
                "environment": "local",
                "uptime_seconds": 10,
            },
            "statistics": {
                "users": 1,
                "students": 1,
                "conveners": 0,
                "companies": 0,
                "hiring_opportunities": 0,
                "applications": 0,
                "notifications": 0,
                "storage_files_approx": 0,
            },
            "notes": ["Read-only"],
        },
    )
    set_cached_health(fake.model_dump(mode="json"))
    result = service.get_system_health(_actor("SUPER_ADMIN"))
    assert result.cached is True
    assert result.overall_status == "healthy"
    assert result.storage.upload_test == "skipped"
    invalidate_health_cache()


def test_upload_test_always_skipped_in_schema_default() -> None:
    from app.modules.admin.health_schemas import StorageHealth

    row = StorageHealth(status="healthy", configured=True)
    assert row.upload_test == "skipped"
