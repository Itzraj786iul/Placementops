import uuid

from sqlalchemy.orm import Session

from app.modules.audit.access import ensure_staff_access
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.exceptions import AuditValidationError
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import (
    AuditListResponse,
    AuditLogResponse,
    build_list_response,
)
from app.modules.users.models import User


class AuditService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AuditRepository(db)

    def list_audit_logs(
        self,
        user: User,
        *,
        page: int = 1,
        page_size: int = 20,
        entity_type: AuditEntityType | None = None,
        action: AuditAction | None = None,
        performed_by: uuid.UUID | None = None,
    ) -> AuditListResponse:
        ensure_staff_access(user)
        self._validate_pagination(page, page_size)
        offset = (page - 1) * page_size
        rows, total = self.repository.list_logs(
            entity_type=entity_type,
            action=action,
            performed_by=performed_by,
            offset=offset,
            limit=page_size,
        )
        items = [AuditLogResponse.model_validate(row) for row in rows]
        return build_list_response(
            items,
            page=page,
            page_size=page_size,
            total=total,
        )

    def list_entity_audit_logs(
        self,
        user: User,
        entity_type: AuditEntityType,
        entity_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> AuditListResponse:
        ensure_staff_access(user)
        self._validate_pagination(page, page_size)
        offset = (page - 1) * page_size
        rows, total = self.repository.list_logs(
            entity_type=entity_type,
            entity_id=entity_id,
            offset=offset,
            limit=page_size,
        )
        items = [AuditLogResponse.model_validate(row) for row in rows]
        return build_list_response(
            items,
            page=page,
            page_size=page_size,
            total=total,
        )

    @staticmethod
    def _validate_pagination(page: int, page_size: int) -> None:
        if page < 1:
            raise AuditValidationError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise AuditValidationError("page_size must be between 1 and 100")
