"""Request-scoped observability context (request ID)."""

from __future__ import annotations

from contextvars import ContextVar

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> None:
    _request_id.set(request_id)


def clear_request_id() -> None:
    _request_id.set(None)


def get_request_id() -> str | None:
    return _request_id.get()
