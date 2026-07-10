from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.applications.service import ApplicationService


def get_application_service(
    db: Session = Depends(get_db_session),
) -> ApplicationService:
    return ApplicationService(db)
