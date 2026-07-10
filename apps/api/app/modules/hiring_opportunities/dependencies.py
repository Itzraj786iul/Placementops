from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.hiring_opportunities.service import HiringOpportunityService


def get_hiring_opportunity_service(
    db: Session = Depends(get_db_session),
) -> HiringOpportunityService:
    return HiringOpportunityService(db)
