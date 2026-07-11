"""Centralized maintenance-mode gate for write operations."""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.modules.admin.maintenance_state import (
    get_maintenance_state,
    user_bypasses_maintenance,
)
from app.platform.auth.jwt import decode_token

WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}

# Always allow these path prefixes (after /api/v1 or absolute)
ALWAYS_ALLOW_PREFIXES = (
    "/health",
    "/api/v1/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/google/callback",
    "/api/v1/auth/google/login",
    "/api/v1/maintenance",
    "/api/v1/admin",
)


class MaintenanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        if request.method == "OPTIONS":
            return await call_next(request)

        path = request.url.path
        if _is_always_allowed(path):
            return await call_next(request)

        state = get_maintenance_state()
        if not state.enabled:
            return await call_next(request)

        # Read-only traffic remains available
        if request.method not in WRITE_METHODS:
            return await call_next(request)

        # Auth session lifecycle: allow logout/refresh; block new logins via service
        if path in {
            "/api/v1/auth/logout",
            "/api/v1/auth/refresh",
        }:
            return await call_next(request)

        if path in {
            "/api/v1/auth/dev/login",
            "/api/v1/auth/exchange",
        }:
            # Login/exchange still run so AuthService can return 503 with message
            return await call_next(request)

        role_names = _resolve_role_names(request)
        if role_names and user_bypasses_maintenance(role_names, state):
            return await call_next(request)

        return JSONResponse(
            status_code=503,
            content={
                "message": state.message,
                "title": state.title,
                "maintenance": True,
                "estimated_completion": state.estimated_completion,
                "support_contact": state.support_contact,
            },
            headers={"Retry-After": "300"},
        )


def _is_always_allowed(path: str) -> bool:
    for prefix in ALWAYS_ALLOW_PREFIXES:
        if path == prefix or path.startswith(prefix + "/"):
            return True
    return False


def _resolve_role_names(request: Request) -> set[str]:
    token = request.cookies.get("access_token")
    auth = request.headers.get("authorization") or ""
    if not token and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()
    if not token:
        return set()

    try:
        payload = decode_token(token, "access")
        user_id = uuid.UUID(str(payload["sub"]))
    except Exception:  # noqa: BLE001
        return set()

    from app.database.session import SessionLocal
    from app.modules.users.models import User

    db = SessionLocal()
    try:
        user = db.get(User, user_id)
        if user is None:
            return set()
        # Ensure roles are loaded
        return {role.name for role in user.roles}
    finally:
        db.close()
