import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Index, String, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.utils.datetime import utc_now

entity_type_enum = Enum(
    AuditEntityType,
    name="audit_entity_type_enum",
    create_constraint=True,
    validate_strings=True,
)
action_enum = Enum(
    AuditAction,
    name="audit_action_enum",
    create_constraint=True,
    validate_strings=True,
)


class AuditLog(Base):
    """Immutable audit record. Never update or delete rows in application code."""

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity_type", "entity_type"),
        Index("ix_audit_logs_entity_id", "entity_id"),
        Index("ix_audit_logs_performed_at", "performed_at"),
        Index("ix_audit_logs_performed_by", "performed_by"),
        Index(
            "ix_audit_logs_entity_lookup",
            "entity_type",
            "entity_id",
            "performed_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[AuditEntityType] = mapped_column(entity_type_enum, nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[AuditAction] = mapped_column(action_enum, nullable=False)
    performed_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    performed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    old_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    new_values: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
