import uuid

from fastapi import APIRouter, Depends, Query, status

from app.modules.applications.dependencies import get_application_service
from app.modules.applications.schemas import (
    ApplicationListItem,
    ApplicationResponse,
    ApplyRequest,
)
from app.modules.applications.service import ApplicationService
from app.modules.hiring_opportunities.dependencies import get_hiring_opportunity_service
from app.modules.hiring_opportunities.enums import OpportunityStatus
from app.modules.hiring_opportunities.schemas import (
    EligibilityRuleResponse,
    EligibilityRuleUpdate,
    OpportunityCreate,
    OpportunityDocumentCreate,
    OpportunityDocumentResponse,
    OpportunityListItem,
    OpportunityResponse,
    OpportunityUpdate,
    TimelineEntryResponse,
    TimelineUpdate,
)
from app.modules.hiring_opportunities.service import HiringOpportunityService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

opportunities_router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@opportunities_router.get("", response_model=list[OpportunityListItem])
def list_opportunities(
    status: OpportunityStatus | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> list[OpportunityListItem]:
    return service.list_opportunities(current_user, status)


@opportunities_router.post(
    "",
    response_model=OpportunityResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_opportunity(
    payload: OpportunityCreate,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> OpportunityResponse:
    return service.create_opportunity(current_user, payload)


@opportunities_router.get("/{opportunity_id}", response_model=OpportunityResponse)
def get_opportunity(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> OpportunityResponse:
    return service.get_opportunity(current_user, opportunity_id)


@opportunities_router.patch("/{opportunity_id}", response_model=OpportunityResponse)
def update_opportunity(
    opportunity_id: uuid.UUID,
    payload: OpportunityUpdate,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> OpportunityResponse:
    return service.update_opportunity(current_user, opportunity_id, payload)


@opportunities_router.post(
    "/{opportunity_id}/publish",
    response_model=OpportunityResponse,
)
def publish_opportunity(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> OpportunityResponse:
    return service.publish_opportunity(current_user, opportunity_id)


@opportunities_router.post(
    "/{opportunity_id}/archive",
    response_model=OpportunityResponse,
)
def archive_opportunity(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> OpportunityResponse:
    return service.archive_opportunity(current_user, opportunity_id)


@opportunities_router.get(
    "/{opportunity_id}/eligibility",
    response_model=EligibilityRuleResponse,
)
def get_eligibility(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> EligibilityRuleResponse:
    return service.get_eligibility(current_user, opportunity_id)


@opportunities_router.patch(
    "/{opportunity_id}/eligibility",
    response_model=EligibilityRuleResponse,
)
def update_eligibility(
    opportunity_id: uuid.UUID,
    payload: EligibilityRuleUpdate,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> EligibilityRuleResponse:
    return service.update_eligibility(current_user, opportunity_id, payload)


@opportunities_router.post(
    "/{opportunity_id}/documents",
    response_model=OpportunityDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_document(
    opportunity_id: uuid.UUID,
    payload: OpportunityDocumentCreate,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> OpportunityDocumentResponse:
    return service.add_document(current_user, opportunity_id, payload)


@opportunities_router.get(
    "/{opportunity_id}/timeline",
    response_model=list[TimelineEntryResponse],
)
def get_timeline(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> list[TimelineEntryResponse]:
    return service.get_timeline(current_user, opportunity_id)


@opportunities_router.patch(
    "/{opportunity_id}/timeline",
    response_model=TimelineEntryResponse,
)
def update_timeline(
    opportunity_id: uuid.UUID,
    payload: TimelineUpdate,
    current_user: User = Depends(get_current_user),
    service: HiringOpportunityService = Depends(get_hiring_opportunity_service),
) -> TimelineEntryResponse:
    return service.update_timeline(current_user, opportunity_id, payload)


@opportunities_router.post(
    "/{opportunity_id}/apply",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["applications"],
)
def apply_to_opportunity(
    opportunity_id: uuid.UUID,
    payload: ApplyRequest,
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    return service.apply_to_opportunity(current_user, opportunity_id, payload)


@opportunities_router.get(
    "/{opportunity_id}/applications",
    response_model=list[ApplicationListItem],
    tags=["applications"],
)
def list_opportunity_applications(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> list[ApplicationListItem]:
    return service.list_opportunity_applications(current_user, opportunity_id)
