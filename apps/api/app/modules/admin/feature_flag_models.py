from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.utils.datetime import utc_now

FLAG_SCOPE_GLOBAL = "GLOBAL"
FLAG_SCOPE_ROLE = "ROLE"
FLAG_SCOPE_DEPARTMENT = "DEPARTMENT"
FLAG_SCOPE_SEASON = "SEASON"

FLAG_SCOPES = {
    FLAG_SCOPE_GLOBAL,
    FLAG_SCOPE_ROLE,
    FLAG_SCOPE_DEPARTMENT,
    FLAG_SCOPE_SEASON,
}


class FeatureFlag(Base):
    __tablename__ = "feature_flags"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(150))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    scope: Mapped[str] = mapped_column(
        String(30),
        default=FLAG_SCOPE_GLOBAL,
        nullable=False,
        index=True,
    )
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    updated_by: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
