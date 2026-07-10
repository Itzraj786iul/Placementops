import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.platform.notifications.enums import (
    DeliveryStatus,
    NotificationEntityType,
    NotificationType,
)
from app.utils.datetime import utc_now

notification_type_enum = Enum(
    NotificationType,
    name="notification_type_enum",
    create_constraint=True,
    validate_strings=True,
)
delivery_status_enum = Enum(
    DeliveryStatus,
    name="notification_delivery_status_enum",
    create_constraint=True,
    validate_strings=True,
)
entity_type_enum = Enum(
    NotificationEntityType,
    name="notification_entity_type_enum",
    create_constraint=True,
    validate_strings=True,
)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        Index("ix_notifications_recipient_user_id", "recipient_user_id"),
        Index("ix_notifications_created_at", "created_at"),
        Index("ix_notifications_is_read", "is_read"),
        Index(
            "ix_notifications_recipient_unread",
            "recipient_user_id",
            "is_read",
            "created_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    recipient_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[NotificationType] = mapped_column(notification_type_enum, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[NotificationEntityType | None] = mapped_column(
        entity_type_enum,
        nullable=True,
    )
    entity_id: Mapped[uuid.UUID | None] = mapped_column(Uuid, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivery_status: Mapped[DeliveryStatus] = mapped_column(
        delivery_status_enum,
        default=DeliveryStatus.PENDING,
        nullable=False,
    )


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
