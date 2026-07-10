from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.companies.service import CompanyService


def get_company_service(db: Session = Depends(get_db_session)) -> CompanyService:
    return CompanyService(db)
