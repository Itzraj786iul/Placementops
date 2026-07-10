"""Request-scoped audit context (IP / user-agent) via contextvars."""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass

_audit_request_context: ContextVar[AuditRequestContext | None] = ContextVar(
    "audit_request_context",
    default=None,
)


@dataclass(frozen=True)
class AuditRequestContext:
    ip_address: str | None = None
    user_agent: str | None = None


def set_audit_request_context(
    ip_address: str | None,
    user_agent: str | None,
) -> None:
    _audit_request_context.set(
        AuditRequestContext(ip_address=ip_address, user_agent=user_agent),
    )


def clear_audit_request_context() -> None:
    _audit_request_context.set(None)


def get_audit_request_context() -> AuditRequestContext:
    return _audit_request_context.get() or AuditRequestContext()
