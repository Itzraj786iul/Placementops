from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.exports.service import ExportService


def get_export_service(db: Session = Depends(get_db_session)) -> ExportService:
    return ExportService(db)
