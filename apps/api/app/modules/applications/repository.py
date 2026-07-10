import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.applications.models import (
    Application,
    ApplicationAnswer,
    ApplicationQuestion,
    ApplicationSnapshot,
)
from app.modules.hiring_opportunities.enums import OpportunityStatus
from app.modules.hiring_opportunities.models import HiringOpportunity


class ApplicationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, application_id: uuid.UUID) -> Application | None:
        stmt = (
            select(Application)
            .options(
                selectinload(Application.student_profile),
                selectinload(Application.answers),
                selectinload(Application.snapshot),
            )
            .where(Application.id == application_id)
        )
        return self.db.scalars(stmt).first()

    def get_by_student_and_opportunity(
        self,
        student_profile_id: uuid.UUID,
        hiring_opportunity_id: uuid.UUID,
    ) -> Application | None:
        stmt = select(Application).where(
            Application.student_profile_id == student_profile_id,
            Application.hiring_opportunity_id == hiring_opportunity_id,
        )
        return self.db.scalars(stmt).first()

    def list_by_student_profile(self, student_profile_id: uuid.UUID) -> list[Application]:
        stmt = (
            select(Application)
            .where(Application.student_profile_id == student_profile_id)
            .order_by(Application.applied_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_by_opportunity(self, hiring_opportunity_id: uuid.UUID) -> list[Application]:
        stmt = (
            select(Application)
            .options(selectinload(Application.student_profile))
            .where(Application.hiring_opportunity_id == hiring_opportunity_id)
            .order_by(Application.applied_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def get_opportunity(self, opportunity_id: uuid.UUID) -> HiringOpportunity | None:
        stmt = (
            select(HiringOpportunity)
            .options(selectinload(HiringOpportunity.eligibility_rule))
            .where(HiringOpportunity.id == opportunity_id)
        )
        return self.db.scalars(stmt).first()

    def list_questions(self, hiring_opportunity_id: uuid.UUID) -> list[ApplicationQuestion]:
        stmt = (
            select(ApplicationQuestion)
            .where(ApplicationQuestion.hiring_opportunity_id == hiring_opportunity_id)
            .order_by(ApplicationQuestion.display_order, ApplicationQuestion.id)
        )
        return list(self.db.scalars(stmt).all())

    def get_question(self, question_id: uuid.UUID) -> ApplicationQuestion | None:
        return self.db.get(ApplicationQuestion, question_id)

    def save_application(self, application: Application) -> Application:
        self.db.add(application)
        self.db.flush()
        return application

    def save_snapshot(self, snapshot: ApplicationSnapshot) -> ApplicationSnapshot:
        self.db.add(snapshot)
        self.db.flush()
        return snapshot

    def save_answer(self, answer: ApplicationAnswer) -> ApplicationAnswer:
        self.db.add(answer)
        self.db.flush()
        return answer

    def opportunity_is_published(self, opportunity_id: uuid.UUID) -> bool:
        stmt = select(HiringOpportunity.status).where(
            HiringOpportunity.id == opportunity_id,
        )
        status = self.db.scalars(stmt).first()
        return status == OpportunityStatus.PUBLISHED
