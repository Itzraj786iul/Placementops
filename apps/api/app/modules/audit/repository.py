import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.models import AuditLog


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, entry: AuditLog) -> AuditLog:
        self.db.add(entry)
        return entry

    def list_logs(
        self,
        *,
        entity_type: AuditEntityType | None = None,
        entity_id: uuid.UUID | None = None,
        action: AuditAction | None = None,
        performed_by: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AuditLog], int]:
        filters = []
        if entity_type is not None:
            filters.append(AuditLog.entity_type == entity_type)
        if entity_id is not None:
            filters.append(AuditLog.entity_id == entity_id)
        if action is not None:
            filters.append(AuditLog.action == action)
        if performed_by is not None:
            filters.append(AuditLog.performed_by == performed_by)

        count_stmt = select(func.count()).select_from(AuditLog)
        list_stmt = select(AuditLog)
        if filters:
            count_stmt = count_stmt.where(*filters)
            list_stmt = list_stmt.where(*filters)

        total = int(self.db.scalar(count_stmt) or 0)
        rows = list(
            self.db.scalars(
                list_stmt.order_by(AuditLog.performed_at.desc(), AuditLog.id.desc())
                .offset(offset)
                .limit(limit)
            ).all()
        )
        return rows, total
