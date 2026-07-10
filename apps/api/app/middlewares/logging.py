from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.modules.audit.context import (
    clear_audit_request_context,
    set_audit_request_context,
)


def _client_ip(request: Request) -> str | None:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    if request.client is not None:
        return request.client.host
    return None


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        set_audit_request_context(
            ip_address=_client_ip(request),
            user_agent=request.headers.get("user-agent"),
        )
        try:
            return await call_next(request)
        finally:
            clear_audit_request_context()
