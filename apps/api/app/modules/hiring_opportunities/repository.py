import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.hiring_opportunities.enums import OpportunityStatus
from app.modules.hiring_opportunities.models import (
    EligibilityRule,
    HiringOpportunity,
    OpportunityDocument,
    OpportunityTimeline,
)
from app.modules.students.models import Department


class HiringOpportunityRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, opportunity_id: uuid.UUID) -> HiringOpportunity | None:
        stmt = (
            select(HiringOpportunity)
            .options(
                selectinload(HiringOpportunity.eligibility_rule),
                selectinload(HiringOpportunity.documents),
                selectinload(HiringOpportunity.timeline_entries),
            )
            .where(HiringOpportunity.id == opportunity_id)
        )
        return self.db.scalars(stmt).first()

    def list_opportunities(
        self,
        status: OpportunityStatus | None = None,
        published_only: bool = False,
    ) -> list[HiringOpportunity]:
        stmt = (
            select(HiringOpportunity)
            .options(selectinload(HiringOpportunity.timeline_entries))
            .order_by(HiringOpportunity.created_at.desc())
        )
        if published_only:
            stmt = stmt.where(HiringOpportunity.status == OpportunityStatus.PUBLISHED)
        elif status is not None:
            stmt = stmt.where(HiringOpportunity.status == status)
        return list(self.db.scalars(stmt).all())

    def save_opportunity(self, opportunity: HiringOpportunity) -> HiringOpportunity:
        self.db.add(opportunity)
        self.db.flush()
        return opportunity

    def save_eligibility(self, rule: EligibilityRule) -> EligibilityRule:
        self.db.add(rule)
        self.db.flush()
        return rule

    def get_eligibility(self, opportunity_id: uuid.UUID) -> EligibilityRule | None:
        stmt = select(EligibilityRule).where(
            EligibilityRule.hiring_opportunity_id == opportunity_id,
        )
        return self.db.scalars(stmt).first()

    def save_document(self, document: OpportunityDocument) -> OpportunityDocument:
        self.db.add(document)
        self.db.flush()
        return document

    def list_documents(self, opportunity_id: uuid.UUID) -> list[OpportunityDocument]:
        stmt = (
            select(OpportunityDocument)
            .where(OpportunityDocument.hiring_opportunity_id == opportunity_id)
            .order_by(OpportunityDocument.uploaded_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def save_timeline_entry(self, entry: OpportunityTimeline) -> OpportunityTimeline:
        self.db.add(entry)
        self.db.flush()
        return entry

    def list_timeline(self, opportunity_id: uuid.UUID) -> list[OpportunityTimeline]:
        stmt = (
            select(OpportunityTimeline)
            .where(OpportunityTimeline.hiring_opportunity_id == opportunity_id)
            .order_by(OpportunityTimeline.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def company_exists(self, company_id: uuid.UUID) -> bool:
        from app.modules.companies.models import Company

        return self.db.get(Company, company_id) is not None

    def departments_exist(self, department_ids: list[uuid.UUID]) -> bool:
        if not department_ids:
            return True
        stmt = select(Department.id).where(Department.id.in_(department_ids))
        found = set(self.db.scalars(stmt).all())
        return len(found) == len(set(department_ids))
