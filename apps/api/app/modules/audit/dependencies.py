from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.audit.service import AuditService


def get_audit_service(db: Session = Depends(get_db_session)) -> AuditService:
    return AuditService(db)
