import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.utils.datetime import utc_now

SEASON_STATUS_PLANNING = "planning"
SEASON_STATUS_ACTIVE = "active"
SEASON_STATUS_COMPLETED = "completed"
SEASON_STATUS_ARCHIVED = "archived"

SEASON_STATUSES = {
    SEASON_STATUS_PLANNING,
    SEASON_STATUS_ACTIVE,
    SEASON_STATUS_COMPLETED,
    SEASON_STATUS_ARCHIVED,
}


class PlacementSeason(Base):
    __tablename__ = "placement_seasons"
    __table_args__ = (
        Index("ix_placement_seasons_status", "status"),
        Index("ix_placement_seasons_is_current", "is_current"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    academic_batch: Mapped[str] = mapped_column(String(50), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default=SEASON_STATUS_PLANNING,
        nullable=False,
    )
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
