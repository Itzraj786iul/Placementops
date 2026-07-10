from __future__ import annotations

import logging
import uuid

from sqlalchemy.orm import Session

from app.modules.users.models import User
from app.platform.notifications.email_service import EmailService
from app.platform.notifications.enums import (
    DeliveryStatus,
    NotificationEntityType,
    NotificationType,
)
from app.platform.notifications.exceptions import (
    NotificationForbiddenError,
    NotificationNotFoundError,
)
from app.platform.notifications.models import Notification
from app.platform.notifications.repository import NotificationRepository
from app.platform.notifications.schemas import (
    MarkAllReadResponse,
    MarkReadResponse,
    NotificationListResponse,
    NotificationPreferenceResponse,
    NotificationPreferenceUpdate,
    NotificationResponse,
)
from app.platform.notifications.template_service import TemplateService

logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(
        self,
        db: Session,
        *,
        repository: NotificationRepository | None = None,
        email_service: EmailService | None = None,
        template_service: TemplateService | None = None,
    ) -> None:
        self.db = db
        self.repository = repository or NotificationRepository(db)
        self.email = email_service or EmailService()
        self.templates = template_service or TemplateService()

    def notify(
        self,
        *,
        recipient: User,
        notification_type: NotificationType,
        context: dict[str, str],
        entity_type: NotificationEntityType | None = None,
        entity_id: uuid.UUID | None = None,
        commit: bool = False,
    ) -> Notification | None:
        """
        Create an in-app notification and optionally send email.

        Respects per-user preferences. Does not raise on email failure.
        """
        prefs = self.repository.get_or_create_preference(recipient.id)
        rendered = self.templates.render(notification_type, context)

        notification: Notification | None = None
        if prefs.in_app_enabled:
            notification = self.repository.add(
                Notification(
                    recipient_user_id=recipient.id,
                    type=notification_type,
                    title=rendered.title[:255],
                    message=rendered.message,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    delivery_status=DeliveryStatus.PENDING,
                ),
            )

        delivery = DeliveryStatus.SKIPPED
        if prefs.email_enabled:
            result = self.email.send(
                to=recipient.college_email,
                subject=rendered.subject,
                html=rendered.html,
                text=rendered.text,
            )
            if result.success:
                delivery = DeliveryStatus.SENT
            elif not self.email.is_configured:
                delivery = DeliveryStatus.SKIPPED
            else:
                delivery = DeliveryStatus.FAILED
                logger.warning(
                    "Email delivery failed for user=%s type=%s: %s",
                    recipient.id,
                    notification_type.value,
                    result.error,
                )
        else:
            delivery = DeliveryStatus.SKIPPED

        if notification is not None:
            self.repository.set_delivery_status(notification, delivery)
        elif prefs.email_enabled and delivery == DeliveryStatus.SENT:
            # Email-only: still record a read notification row for history? Skip.
            pass

        if commit:
            self.db.commit()
        return notification

    def list_notifications(
        self,
        user: User,
        *,
        page: int = 1,
        page_size: int = 20,
        unread_only: bool = False,
    ) -> NotificationListResponse:
        page_data = self.repository.list_for_user(
            user.id,
            page=page,
            page_size=page_size,
            unread_only=unread_only,
        )
        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in page_data.items],
            total=page_data.total,
            unread_count=page_data.unread_count,
            page=page,
            page_size=page_size,
        )

    def mark_read(self, user: User, notification_id: uuid.UUID) -> MarkReadResponse:
        notification = self.repository.get_by_id(notification_id)
        if notification is None:
            raise NotificationNotFoundError()
        if notification.recipient_user_id != user.id:
            raise NotificationForbiddenError()
        updated = self.repository.mark_read(notification)
        self.db.commit()
        return MarkReadResponse(
            id=updated.id,
            is_read=updated.is_read,
            read_at=updated.read_at,
        )

    def mark_all_read(self, user: User) -> MarkAllReadResponse:
        updated = self.repository.mark_all_read(user.id)
        self.db.commit()
        return MarkAllReadResponse(updated=updated)

    def get_preferences(self, user: User) -> NotificationPreferenceResponse:
        pref = self.repository.get_or_create_preference(user.id)
        self.db.commit()
        return NotificationPreferenceResponse.model_validate(pref)

    def update_preferences(
        self,
        user: User,
        payload: NotificationPreferenceUpdate,
    ) -> NotificationPreferenceResponse:
        pref = self.repository.get_or_create_preference(user.id)
        if payload.email_enabled is not None:
            pref.email_enabled = payload.email_enabled
        if payload.in_app_enabled is not None:
            pref.in_app_enabled = payload.in_app_enabled
        self.db.commit()
        return NotificationPreferenceResponse.model_validate(pref)
