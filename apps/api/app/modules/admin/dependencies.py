from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.admin.service import AdminUserService


def get_admin_user_service(
    db: Session = Depends(get_db_session),
) -> AdminUserService:
    return AdminUserService(db)
