from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.imports.service import ImportService


def get_import_service(db: Session = Depends(get_db_session)) -> ImportService:
    return ImportService(db)
