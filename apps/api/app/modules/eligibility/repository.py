import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.applications.models import Application
from app.modules.hiring_opportunities.models import EligibilityRule, HiringOpportunity
from app.modules.students.models import StudentProfile


class EligibilityRepository:
    """Repository layer — fetch only. No evaluation logic."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_opportunity(self, opportunity_id: uuid.UUID) -> HiringOpportunity | None:
        stmt = (
            select(HiringOpportunity)
            .options(selectinload(HiringOpportunity.eligibility_rule))
            .where(HiringOpportunity.id == opportunity_id)
        )
        return self.db.scalars(stmt).first()

    def get_eligibility_rule(self, opportunity_id: uuid.UUID) -> EligibilityRule | None:
        stmt = select(EligibilityRule).where(
            EligibilityRule.hiring_opportunity_id == opportunity_id,
        )
        return self.db.scalars(stmt).first()

    def get_profile(self, profile_id: uuid.UUID) -> StudentProfile | None:
        stmt = (
            select(StudentProfile)
            .options(
                selectinload(StudentProfile.department),
                selectinload(StudentProfile.personal_information),
                selectinload(StudentProfile.academic_information),
                selectinload(StudentProfile.education_history),
            )
            .where(StudentProfile.id == profile_id)
        )
        return self.db.scalars(stmt).first()

    def list_application_profile_ids(
        self,
        opportunity_id: uuid.UUID,
    ) -> list[uuid.UUID]:
        stmt = (
            select(Application.student_profile_id)
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
