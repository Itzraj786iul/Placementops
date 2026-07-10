from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.modules.audit.context import get_audit_request_context
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.models import AuditLog
from app.modules.audit.serialize import json_safe


def record_audit(
    db: Session,
    *,
    entity_type: AuditEntityType,
    entity_id: uuid.UUID,
    action: AuditAction,
    performed_by: uuid.UUID,
    old_values: dict[str, Any] | None = None,
    new_values: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> AuditLog:
    """Append an immutable audit row to the current session (observer only)."""
    ctx = get_audit_request_context()
    entry = AuditLog(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        performed_by=performed_by,
        old_values=json_safe(old_values) if old_values is not None else None,
        new_values=json_safe(new_values) if new_values is not None else None,
        metadata_=json_safe(metadata) if metadata is not None else None,
        ip_address=ip_address if ip_address is not None else ctx.ip_address,
        user_agent=user_agent if user_agent is not None else ctx.user_agent,
    )
    if entry.user_agent and len(entry.user_agent) > 512:
        entry.user_agent = entry.user_agent[:512]
    if entry.ip_address and len(entry.ip_address) > 64:
        entry.ip_address = entry.ip_address[:64]
    db.add(entry)
    return entry
