import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.applications.models import Application
from app.modules.companies.models import Company
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.students.models import StudentProfile


class ExportRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_opportunity(self, opportunity_id: uuid.UUID) -> HiringOpportunity | None:
        stmt = (
            select(HiringOpportunity)
            .options(selectinload(HiringOpportunity.eligibility_rule))
            .where(HiringOpportunity.id == opportunity_id)
        )
        return self.db.scalars(stmt).first()

    def get_company_name(self, company_id: uuid.UUID) -> str | None:
        stmt = select(Company.name).where(Company.id == company_id)
        return self.db.scalars(stmt).first()

    def list_applications_with_snapshots(
        self,
        opportunity_id: uuid.UUID,
    ) -> list[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.snapshot))
            .where(Application.hiring_opportunity_id == opportunity_id)
            .order_by(Application.applied_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_profiles_by_ids(
        self,
        profile_ids: list[uuid.UUID],
    ) -> list[StudentProfile]:
        if not profile_ids:
            return []
        stmt = (
            select(StudentProfile)
            .options(
                selectinload(StudentProfile.department),
                selectinload(StudentProfile.personal_information),
                selectinload(StudentProfile.academic_information),
                selectinload(StudentProfile.education_history),
            )
            .where(StudentProfile.id.in_(profile_ids))
        )
        return list(self.db.scalars(stmt).all())
