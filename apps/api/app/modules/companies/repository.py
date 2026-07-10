import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.companies.enums import CompanyStatus
from app.modules.companies.models import (
    Company,
    CompanyCommunication,
    CompanyContact,
    CompanyDocument,
    CompanyHandler,
    CompanyPipeline,
)


class CompanyRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_company_by_id(self, company_id: uuid.UUID) -> Company | None:
        stmt = (
            select(Company)
            .options(
                selectinload(Company.pipeline),
                selectinload(Company.handlers),
                selectinload(Company.contacts),
                selectinload(Company.communications),
                selectinload(Company.documents),
            )
            .where(Company.id == company_id)
        )
        return self.db.scalars(stmt).first()

    def list_companies(self, status: CompanyStatus | None = None) -> list[Company]:
        stmt = (
            select(Company)
            .options(
                selectinload(Company.pipeline),
                selectinload(Company.handlers),
            )
            .order_by(Company.name)
        )
        if status is not None:
            stmt = stmt.where(Company.status == status)
        return list(self.db.scalars(stmt).all())

    def company_name_exists(self, name: str, exclude_id: uuid.UUID | None = None) -> bool:
        stmt = select(Company.id).where(Company.name == name)
        if exclude_id is not None:
            stmt = stmt.where(Company.id != exclude_id)
        return self.db.scalars(stmt).first() is not None

    def save_company(self, company: Company) -> Company:
        self.db.add(company)
        self.db.flush()
        return company

    def save_pipeline(self, pipeline: CompanyPipeline) -> CompanyPipeline:
        self.db.add(pipeline)
        self.db.flush()
        return pipeline

    def save_handler(self, handler: CompanyHandler) -> CompanyHandler:
        self.db.add(handler)
        self.db.flush()
        return handler

    def get_active_handler(self, company_id: uuid.UUID) -> CompanyHandler | None:
        stmt = select(CompanyHandler).where(
            CompanyHandler.company_id == company_id,
            CompanyHandler.is_active.is_(True),
        )
        return self.db.scalars(stmt).first()

    def save_contact(self, contact: CompanyContact) -> CompanyContact:
        self.db.add(contact)
        self.db.flush()
        return contact

    def list_contacts(self, company_id: uuid.UUID) -> list[CompanyContact]:
        stmt = (
            select(CompanyContact)
            .where(CompanyContact.company_id == company_id)
            .order_by(CompanyContact.is_primary.desc(), CompanyContact.name)
        )
        return list(self.db.scalars(stmt).all())

    def save_communication(
        self,
        communication: CompanyCommunication,
    ) -> CompanyCommunication:
        self.db.add(communication)
        self.db.flush()
        return communication

    def list_communications(self, company_id: uuid.UUID) -> list[CompanyCommunication]:
        stmt = (
            select(CompanyCommunication)
            .where(CompanyCommunication.company_id == company_id)
            .order_by(CompanyCommunication.communication_date.desc())
        )
        return list(self.db.scalars(stmt).all())

    def save_document(self, document: CompanyDocument) -> CompanyDocument:
        self.db.add(document)
        self.db.flush()
        return document

    def clear_primary_contacts(self, company_id: uuid.UUID) -> None:
        stmt = select(CompanyContact).where(
            CompanyContact.company_id == company_id,
            CompanyContact.is_primary.is_(True),
        )
        for contact in self.db.scalars(stmt).all():
            contact.is_primary = False
