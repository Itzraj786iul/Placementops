import uuid

from sqlalchemy.orm import Session

from app.modules.companies.access import ensure_staff_access
from app.modules.companies.enums import CompanyStatus, PipelineStage
from app.modules.companies.exceptions import (
    CompanyConflictError,
    CompanyNotFoundError,
    CompanyValidationError,
)
from app.modules.companies.models import (
    Company,
    CompanyCommunication,
    CompanyContact,
    CompanyDocument,
    CompanyHandler,
    CompanyPipeline,
)
from app.modules.companies.repository import CompanyRepository
from app.modules.companies.schemas import (
    CommunicationCreate,
    CommunicationResponse,
    CompanyContactCreate,
    CompanyContactResponse,
    CompanyCreate,
    CompanyHandlerResponse,
    CompanyListItem,
    CompanyPipelineResponse,
    CompanyResponse,
    CompanyUpdate,
    DocumentCreate,
    DocumentResponse,
    HandlerAssignment,
    PipelineUpdate,
    TimelineEntry,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.audit.serialize import snapshot_fields
from app.modules.users.models import User
from app.utils.datetime import utc_now

_COMPANY_AUDIT_FIELDS = [
    "name",
    "industry",
    "website",
    "linkedin",
    "headquarters",
    "company_type",
    "status",
]


class CompanyService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = CompanyRepository(db)

    def list_companies(
        self,
        user: User,
        status: CompanyStatus | None = None,
    ) -> list[CompanyListItem]:
        ensure_staff_access(user)
        companies = self.repository.list_companies(status)
        return [self._list_item(company) for company in companies]

    def create_company(self, user: User, payload: CompanyCreate) -> CompanyResponse:
        ensure_staff_access(user)
        if self.repository.company_name_exists(payload.name):
            raise CompanyConflictError("A company with this name already exists")

        company = Company(
            name=payload.name,
            industry=payload.industry,
            website=payload.website,
            linkedin=payload.linkedin,
            headquarters=payload.headquarters,
            company_type=payload.company_type,
            status=CompanyStatus.ACTIVE,
            created_by=user.id,
        )
        self.repository.save_company(company)

        pipeline = CompanyPipeline(
            company_id=company.id,
            current_stage=PipelineStage.NOT_CONTACTED,
            updated_by=user.id,
        )
        self.repository.save_pipeline(pipeline)

        if payload.handler:
            self._assign_handler(company.id, user, payload.handler)

        record_audit(
            self.db,
            entity_type=AuditEntityType.COMPANY,
            entity_id=company.id,
            action=AuditAction.CREATE,
            performed_by=user.id,
            new_values=snapshot_fields(company, _COMPANY_AUDIT_FIELDS),
        )
        self.db.commit()
        return self._company_response(self.repository.get_company_by_id(company.id))

    def get_company(self, user: User, company_id: uuid.UUID) -> CompanyResponse:
        ensure_staff_access(user)
        company = self._get_company_or_raise(company_id)
        return self._company_response(company)

    def update_company(
        self,
        user: User,
        company_id: uuid.UUID,
        payload: CompanyUpdate,
    ) -> CompanyResponse:
        ensure_staff_access(user)
        company = self._get_company_or_raise(company_id)
        old_values = snapshot_fields(company, _COMPANY_AUDIT_FIELDS)
        previous_status = company.status

        if payload.name and payload.name != company.name:
            if self.repository.company_name_exists(payload.name, exclude_id=company_id):
                raise CompanyConflictError("A company with this name already exists")
            company.name = payload.name

        if payload.industry is not None:
            company.industry = payload.industry
        if payload.website is not None:
            company.website = payload.website
        if payload.linkedin is not None:
            company.linkedin = payload.linkedin
        if payload.headquarters is not None:
            company.headquarters = payload.headquarters
        if payload.company_type is not None:
            company.company_type = payload.company_type
        if payload.status is not None:
            company.status = payload.status

        if payload.handler:
            self._assign_handler(company_id, user, payload.handler)

        company.updated_at = utc_now()
        new_values = snapshot_fields(company, _COMPANY_AUDIT_FIELDS)
        action = AuditAction.UPDATE
        if (
            previous_status != CompanyStatus.INACTIVE
            and company.status == CompanyStatus.INACTIVE
        ):
            action = AuditAction.ARCHIVE
        record_audit(
            self.db,
            entity_type=AuditEntityType.COMPANY,
            entity_id=company.id,
            action=action,
            performed_by=user.id,
            old_values=old_values,
            new_values=new_values,
        )
        self.db.commit()
        return self._company_response(self.repository.get_company_by_id(company_id))

    def list_contacts(
        self,
        user: User,
        company_id: uuid.UUID,
    ) -> list[CompanyContactResponse]:
        ensure_staff_access(user)
        self._get_company_or_raise(company_id)
        return [
            CompanyContactResponse.model_validate(contact)
            for contact in self.repository.list_contacts(company_id)
        ]

    def add_contact(
        self,
        user: User,
        company_id: uuid.UUID,
        payload: CompanyContactCreate,
    ) -> CompanyContactResponse:
        ensure_staff_access(user)
        self._get_company_or_raise(company_id)

        if payload.is_primary:
            self.repository.clear_primary_contacts(company_id)

        contact = CompanyContact(
            company_id=company_id,
            name=payload.name,
            designation=payload.designation,
            email=str(payload.email) if payload.email else None,
            phone=payload.phone,
            linkedin=payload.linkedin,
            is_primary=payload.is_primary,
            notes=payload.notes,
        )
        self.repository.save_contact(contact)
        self.db.commit()
        return CompanyContactResponse.model_validate(contact)

    def update_pipeline(
        self,
        user: User,
        company_id: uuid.UUID,
        payload: PipelineUpdate,
    ) -> CompanyPipelineResponse:
        ensure_staff_access(user)
        company = self._get_company_or_raise(company_id)
        if company.pipeline is None:
            raise CompanyValidationError("Company pipeline not initialized")

        company.pipeline.current_stage = payload.current_stage
        company.pipeline.last_updated = utc_now()
        company.pipeline.updated_by = user.id
        company.updated_at = utc_now()
        self.db.commit()
        return CompanyPipelineResponse.model_validate(company.pipeline)

    def add_communication(
        self,
        user: User,
        company_id: uuid.UUID,
        payload: CommunicationCreate,
    ) -> CommunicationResponse:
        ensure_staff_access(user)
        self._get_company_or_raise(company_id)

        communication = CompanyCommunication(
            company_id=company_id,
            type=payload.type,
            subject=payload.subject,
            description=payload.description,
            communication_date=payload.communication_date,
            created_by=user.id,
        )
        self.repository.save_communication(communication)
        self.db.commit()
        return CommunicationResponse.model_validate(communication)

    def get_timeline(self, user: User, company_id: uuid.UUID) -> list[TimelineEntry]:
        ensure_staff_access(user)
        self._get_company_or_raise(company_id)
        return [
            TimelineEntry(
                id=entry.id,
                type=entry.type,
                subject=entry.subject,
                description=entry.description,
                communication_date=entry.communication_date,
                created_by=entry.created_by,
                created_at=entry.created_at,
            )
            for entry in self.repository.list_communications(company_id)
        ]

    def add_document(
        self,
        user: User,
        company_id: uuid.UUID,
        payload: DocumentCreate,
    ) -> DocumentResponse:
        ensure_staff_access(user)
        self._get_company_or_raise(company_id)

        document = CompanyDocument(
            company_id=company_id,
            document_type=payload.document_type,
            file_url=payload.file_url,
            uploaded_by=user.id,
        )
        self.repository.save_document(document)
        self.db.commit()
        return DocumentResponse.model_validate(document)

    def _assign_handler(
        self,
        company_id: uuid.UUID,
        user: User,
        assignment: HandlerAssignment,
    ) -> None:
        active = self.repository.get_active_handler(company_id)
        if active is not None:
            if active.handler_user_id == assignment.handler_user_id:
                active.branch = assignment.branch
                active.ownership_type = assignment.ownership_type
                return
            active.is_active = False
            active.ended_at = utc_now()

        handler = CompanyHandler(
            company_id=company_id,
            handler_user_id=assignment.handler_user_id,
            branch=assignment.branch,
            ownership_type=assignment.ownership_type,
            assigned_by=user.id,
            is_active=True,
        )
        self.repository.save_handler(handler)

    def _get_company_or_raise(self, company_id: uuid.UUID) -> Company:
        company = self.repository.get_company_by_id(company_id)
        if company is None:
            raise CompanyNotFoundError()
        return company

    def _active_handler(self, company: Company) -> CompanyHandlerResponse | None:
        active = next((h for h in company.handlers if h.is_active), None)
        if active is None:
            return None
        return CompanyHandlerResponse.model_validate(active)

    def _company_response(self, company: Company | None) -> CompanyResponse:
        if company is None:
            raise CompanyNotFoundError()
        return CompanyResponse(
            id=company.id,
            name=company.name,
            industry=company.industry,
            website=company.website,
            linkedin=company.linkedin,
            headquarters=company.headquarters,
            company_type=company.company_type,
            status=company.status,
            created_by=company.created_by,
            created_at=company.created_at,
            updated_at=company.updated_at,
            pipeline=(
                CompanyPipelineResponse.model_validate(company.pipeline)
                if company.pipeline
                else None
            ),
            active_handler=self._active_handler(company),
        )

    def _list_item(self, company: Company) -> CompanyListItem:
        return CompanyListItem(
            id=company.id,
            name=company.name,
            industry=company.industry,
            company_type=company.company_type,
            status=company.status,
            created_at=company.created_at,
            pipeline=(
                CompanyPipelineResponse.model_validate(company.pipeline)
                if company.pipeline
                else None
            ),
            active_handler=self._active_handler(company),
        )
