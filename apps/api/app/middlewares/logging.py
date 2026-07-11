"""Request ID assignment, audit context, and structured access logging."""

from __future__ import annotations

import logging
import re
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, log_json
from app.core.request_context import clear_request_id, set_request_id
from app.modules.audit.context import (
    clear_audit_request_context,
    set_audit_request_context,
)

logger = get_logger("placementos.request")

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9\-_]{8,64}$")
REQUEST_ID_HEADER = "X-Request-ID"


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    if request.client is not None:
        return request.client.host
    return None


def resolve_request_id(request: Request) -> str:
    incoming = (request.headers.get("x-request-id") or "").strip()
    if incoming and _REQUEST_ID_RE.fullmatch(incoming):
        return incoming
    return str(uuid.uuid4())


def _optional_user_id(request: Request) -> str | None:
    token = request.cookies.get("access_token")
    auth = request.headers.get("authorization") or ""
    if not token and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1].strip()
    if not token:
        return None
    try:
        from app.platform.auth.jwt import decode_token

        payload = decode_token(token, "access")
        return str(payload.get("sub"))
    except Exception:  # noqa: BLE001 — logging must never fail the request
        return None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        request_id = resolve_request_id(request)
        set_request_id(request_id)
        request.state.request_id = request_id

        ip_address = _client_ip(request)
        set_audit_request_context(
            ip_address=ip_address,
            user_agent=request.headers.get("user-agent"),
        )

        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            try:
                log_json(
                    logger,
                    logging.INFO,
                    event="http.request",
                    request_id=request_id,
                    method=request.method,
                    path=request.url.path,
                    status=status_code,
                    duration_ms=duration_ms,
                    user_id=_optional_user_id(request),
                    ip=ip_address,
                )
            except Exception:  # noqa: BLE001
                pass
            clear_audit_request_context()
            clear_request_id()
