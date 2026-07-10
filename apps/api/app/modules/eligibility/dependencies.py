from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.eligibility.service import EligibilityService


def get_eligibility_service(
    db: Session = Depends(get_db_session),
) -> EligibilityService:
    return EligibilityService(db)
