import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.companies.dependencies import get_company_service
from app.modules.companies.enums import CompanyStatus
from app.modules.companies.schemas import (
    CommunicationCreate,
    CommunicationResponse,
    CompanyContactCreate,
    CompanyContactResponse,
    CompanyCreate,
    CompanyListItem,
    CompanyPipelineResponse,
    CompanyResponse,
    CompanyUpdate,
    DocumentCreate,
    DocumentResponse,
    PipelineUpdate,
    TimelineEntry,
)
from app.modules.companies.service import CompanyService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

companies_router = APIRouter(prefix="/companies", tags=["companies"])


@companies_router.get("", response_model=list[CompanyListItem])
def list_companies(
    status: CompanyStatus | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> list[CompanyListItem]:
    return service.list_companies(current_user, status)


@companies_router.post(
    "",
    response_model=CompanyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_company(
    payload: CompanyCreate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    return service.create_company(current_user, payload)


@companies_router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    return service.get_company(current_user, company_id)


@companies_router.patch("/{company_id}", response_model=CompanyResponse)
def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyResponse:
    return service.update_company(current_user, company_id, payload)


@companies_router.get("/{company_id}/timeline", response_model=list[TimelineEntry])
def get_timeline(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> list[TimelineEntry]:
    return service.get_timeline(current_user, company_id)


@companies_router.get("/{company_id}/contacts", response_model=list[CompanyContactResponse])
def list_contacts(
    company_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> list[CompanyContactResponse]:
    return service.list_contacts(current_user, company_id)


@companies_router.post(
    "/{company_id}/contacts",
    response_model=CompanyContactResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_contact(
    company_id: uuid.UUID,
    payload: CompanyContactCreate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyContactResponse:
    return service.add_contact(current_user, company_id, payload)


@companies_router.patch(
    "/{company_id}/pipeline",
    response_model=CompanyPipelineResponse,
)
def update_pipeline(
    company_id: uuid.UUID,
    payload: PipelineUpdate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CompanyPipelineResponse:
    return service.update_pipeline(current_user, company_id, payload)


@companies_router.post(
    "/{company_id}/communications",
    response_model=CommunicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_communication(
    company_id: uuid.UUID,
    payload: CommunicationCreate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> CommunicationResponse:
    return service.add_communication(current_user, company_id, payload)


@companies_router.post(
    "/{company_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_document(
    company_id: uuid.UUID,
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    service: CompanyService = Depends(get_company_service),
) -> DocumentResponse:
    return service.add_document(current_user, company_id, payload)
