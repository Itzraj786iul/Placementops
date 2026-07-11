"""Startup diagnostics — safe operational snapshot (no secrets)."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import text

from app.core.config import settings
from app.core.logging import get_logger, log_json
from app.modules.admin.feature_flag_catalog import FLAG_DEFAULTS
from app.modules.admin.maintenance_state import get_maintenance_state

logger = get_logger("placementos.startup")


def _database_host() -> str:
    try:
        parsed = urlparse(settings.DATABASE_URL)
        host = parsed.hostname or "unknown"
        db = (parsed.path or "").lstrip("/") or "unknown"
        return f"{host}/{db}"
    except Exception:  # noqa: BLE001
        return "unparseable"


def _google_oauth_ready() -> bool:
    client_id = settings.GOOGLE_CLIENT_ID.strip()
    client_secret = settings.GOOGLE_CLIENT_SECRET.strip()
    if not client_id or not client_secret:
        return False
    if "your-" in client_id.lower() or "your-" in client_secret.lower():
        return False
    if "****" in client_id or "****" in client_secret:
        return False
    return len(client_secret) >= 16


def _probe_database() -> dict[str, Any]:
    try:
        from app.database.session import SessionLocal

        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return {"configured": True, "reachable": True, "target": _database_host()}
        finally:
            db.close()
    except Exception as exc:  # noqa: BLE001 — diagnostics must not raise
        return {
            "configured": True,
            "reachable": False,
            "target": _database_host(),
            "detail": type(exc).__name__,
        }


def _feature_flag_snapshot() -> dict[str, Any]:
    try:
        from app.database.session import SessionLocal
        from app.modules.admin.feature_flag_repository import FeatureFlagRepository

        db = SessionLocal()
        try:
            rows = FeatureFlagRepository(db).list_all()
            overrides = {row.key: bool(row.enabled) for row in rows}
        finally:
            db.close()
    except Exception:  # noqa: BLE001
        overrides = {}

    enabled = 0
    disabled = 0
    for key, meta in FLAG_DEFAULTS.items():
        is_on = overrides.get(key, bool(meta.get("enabled", True)))
        if is_on:
            enabled += 1
        else:
            disabled += 1

    return {
        "known_flags": len(FLAG_DEFAULTS),
        "enabled": enabled,
        "disabled": disabled,
        "db_overrides": len(overrides),
    }


def log_startup_diagnostics() -> None:
    maintenance = get_maintenance_state()
    payload: dict[str, Any] = {
        "event": "startup.diagnostics",
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "api_docs_enabled": settings.api_docs_enabled,
        "cookie_secure": settings.COOKIE_SECURE,
        "dev_login_enabled": settings.ENABLE_DEV_LOGIN,
        "database": _probe_database(),
        "storage": {
            "provider": "cloudinary",
            "configured": settings.cloudinary_configured,
        },
        "email": {
            "provider": settings.EMAIL_PROVIDER,
            "configured": settings.email_configured,
        },
        "oauth": {
            "provider": "google",
            "configured": _google_oauth_ready(),
        },
        "feature_flags": _feature_flag_snapshot(),
        "maintenance_mode": {
            "enabled": maintenance.enabled,
            "title": maintenance.title if maintenance.enabled else None,
        },
    }
    log_json(logger, logging.INFO, **payload)
