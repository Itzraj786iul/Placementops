import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.platform.notifications.enums import (
    DeliveryStatus,
    NotificationEntityType,
    NotificationType,
)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipient_user_id: uuid.UUID
    type: NotificationType
    title: str
    message: str
    entity_type: NotificationEntityType | None
    entity_id: uuid.UUID | None
    is_read: bool
    created_at: datetime
    read_at: datetime | None
    delivery_status: DeliveryStatus


class NotificationListResponse(BaseModel):
    items: list[NotificationResponse]
    total: int
    unread_count: int
    page: int
    page_size: int


class NotificationPreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email_enabled: bool
    in_app_enabled: bool


class NotificationPreferenceUpdate(BaseModel):
    email_enabled: bool | None = None
    in_app_enabled: bool | None = None


class MarkReadResponse(BaseModel):
    id: uuid.UUID
    is_read: bool
    read_at: datetime | None


class MarkAllReadResponse(BaseModel):
    updated: int = Field(ge=0)
