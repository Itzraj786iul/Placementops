"""Standard API error payload helpers."""

from __future__ import annotations

from typing import Any

from app.core.request_context import get_request_id
from app.platform.exceptions import ApplicationError, error_code_from_class_name

STATUS_ERROR_CODES: dict[int, str] = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
    500: "INTERNAL_ERROR",
    502: "BAD_GATEWAY",
    503: "SERVICE_UNAVAILABLE",
}


def error_code_for_exception(exc: BaseException) -> str:
    if isinstance(exc, ApplicationError) and exc.error_code:
        return exc.error_code
    return error_code_from_class_name(type(exc).__name__)


def error_code_for_status(status_code: int) -> str:
    return STATUS_ERROR_CODES.get(status_code, f"HTTP_{status_code}")


def build_error_body(
    *,
    message: str,
    error_code: str,
    request_id: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "error_code": error_code,
        "message": message,
        "request_id": request_id if request_id is not None else get_request_id(),
    }
    for key, value in extra.items():
        if value is not None:
            body[key] = value
    return body
