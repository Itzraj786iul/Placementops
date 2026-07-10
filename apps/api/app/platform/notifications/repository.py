from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.platform.notifications.enums import DeliveryStatus
from app.platform.notifications.models import Notification, NotificationPreference
from app.utils.datetime import utc_now


@dataclass(frozen=True)
class NotificationPage:
    items: list[Notification]
    total: int
    unread_count: int


class NotificationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, notification: Notification) -> Notification:
        self.db.add(notification)
        self.db.flush()
        return notification

    def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        return self.db.get(Notification, notification_id)

    def list_for_user(
        self,
        user_id: uuid.UUID,
        *,
        page: int,
        page_size: int,
        unread_only: bool = False,
    ) -> NotificationPage:
        filters = [Notification.recipient_user_id == user_id]
        if unread_only:
            filters.append(Notification.is_read.is_(False))

        total = self.db.scalar(
            select(func.count()).select_from(Notification).where(*filters),
        ) or 0
        unread_count = self.db.scalar(
            select(func.count())
            .select_from(Notification)
            .where(
                Notification.recipient_user_id == user_id,
                Notification.is_read.is_(False),
            ),
        ) or 0

        stmt = (
            select(Notification)
            .where(*filters)
            .order_by(Notification.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = list(self.db.scalars(stmt).all())
        return NotificationPage(items=items, total=int(total), unread_count=int(unread_count))

    def mark_read(self, notification: Notification) -> Notification:
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = utc_now()
            self.db.flush()
        return notification

    def mark_all_read(self, user_id: uuid.UUID) -> int:
        result = self.db.execute(
            update(Notification)
            .where(
                Notification.recipient_user_id == user_id,
                Notification.is_read.is_(False),
            )
            .values(is_read=True, read_at=utc_now()),
        )
        return int(result.rowcount or 0)

    def get_preference(self, user_id: uuid.UUID) -> NotificationPreference | None:
        stmt = select(NotificationPreference).where(
            NotificationPreference.user_id == user_id,
        )
        return self.db.scalars(stmt).first()

    def get_or_create_preference(self, user_id: uuid.UUID) -> NotificationPreference:
        existing = self.get_preference(user_id)
        if existing is not None:
            return existing
        pref = NotificationPreference(user_id=user_id)
        self.db.add(pref)
        self.db.flush()
        return pref

    def set_delivery_status(
        self,
        notification: Notification,
        status: DeliveryStatus,
    ) -> None:
        notification.delivery_status = status
        self.db.flush()
