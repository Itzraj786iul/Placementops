import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user
from app.platform.notifications.dependencies import get_notification_service
from app.platform.notifications.notification_service import NotificationService
from app.platform.notifications.schemas import (
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
)

notifications_router = APIRouter(prefix="/notifications", tags=["notifications"])


@notifications_router.get("", response_model=NotificationListResponse)
def list_notifications(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=50),
    unread_only: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    return service.list_notifications(
        current_user,
        page=page,
        page_size=page_size,
        unread_only=unread_only,
    )


@notifications_router.patch("/read-all", response_model=MarkAllReadResponse)
def mark_all_notifications_read(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> MarkAllReadResponse:
    return service.mark_all_read(current_user)


@notifications_router.get(
    "/preferences",
    response_model=NotificationPreferenceResponse,
)
def get_notification_preferences(
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationPreferenceResponse:
    return service.get_preferences(current_user)


@notifications_router.patch(
    "/preferences",
    response_model=NotificationPreferenceResponse,
)
def update_notification_preferences(
    payload: NotificationPreferenceUpdate,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationPreferenceResponse:
    return service.update_preferences(current_user, payload)


@notifications_router.patch(
    "/{notification_id}/read",
    response_model=MarkReadResponse,
)
def mark_notification_read(
    notification_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: NotificationService = Depends(get_notification_service),
) -> MarkReadResponse:
    return service.mark_read(current_user, notification_id)
