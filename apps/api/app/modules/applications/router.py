import uuid

from fastapi import APIRouter, Depends, status

from app.modules.applications.dependencies import get_application_service
from app.modules.applications.schemas import (
    ApplicationListItem,
    ApplicationResponse,
    ApplicationSnapshotResponse,
    ApplicationStatusUpdate,
)
from app.modules.applications.service import ApplicationService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

applications_router = APIRouter(prefix="/applications", tags=["applications"])


@applications_router.get("/me", response_model=list[ApplicationListItem])
def list_my_applications(
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> list[ApplicationListItem]:
    return service.list_my_applications(current_user)


@applications_router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    return service.get_application(current_user, application_id)


@applications_router.post(
    "/{application_id}/withdraw",
    response_model=ApplicationResponse,
)
def withdraw_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    return service.withdraw_application(current_user, application_id)


@applications_router.patch(
    "/{application_id}/status",
    response_model=ApplicationResponse,
)
def update_application_status(
    application_id: uuid.UUID,
    payload: ApplicationStatusUpdate,
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationResponse:
    return service.update_application_status(current_user, application_id, payload)


@applications_router.get(
    "/{application_id}/snapshot",
    response_model=ApplicationSnapshotResponse,
)
def get_application_snapshot(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: ApplicationService = Depends(get_application_service),
) -> ApplicationSnapshotResponse:
    return service.get_application_snapshot(current_user, application_id)
