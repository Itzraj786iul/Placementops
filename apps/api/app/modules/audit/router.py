import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.audit.dependencies import get_audit_service
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.schemas import AuditListResponse
from app.modules.audit.service import AuditService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

audit_router = APIRouter(prefix="/audit", tags=["audit"])


@audit_router.get("", response_model=AuditListResponse)
def list_audit_logs(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    entity_type: AuditEntityType | None = Query(default=None),
    action: AuditAction | None = Query(default=None),
    performed_by: uuid.UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service),
) -> AuditListResponse:
    """Staff-only: paginated audit log (newest first)."""
    return service.list_audit_logs(
        current_user,
        page=page,
        page_size=page_size,
        entity_type=entity_type,
        action=action,
        performed_by=performed_by,
    )


@audit_router.get(
    "/entity/{entity_type}/{entity_id}",
    response_model=AuditListResponse,
)
def list_entity_audit_logs(
    entity_type: AuditEntityType,
    entity_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: AuditService = Depends(get_audit_service),
) -> AuditListResponse:
    """Staff-only: audit history for a single entity (newest first)."""
    return service.list_entity_audit_logs(
        current_user,
        entity_type,
        entity_id,
        page=page,
        page_size=page_size,
    )
