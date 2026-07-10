import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.applications.enums import ApplicationStatus
from app.modules.applications.models import application_status_enum
from app.modules.imports.enums import ImportStatus, MatchField, RowMatchStatus
from app.utils.datetime import utc_now

match_field_enum = Enum(
    MatchField,
    name="shortlist_match_field_enum",
    create_constraint=True,
    validate_strings=True,
)
import_status_enum = Enum(
    ImportStatus,
    name="shortlist_import_status_enum",
    create_constraint=True,
    validate_strings=True,
)
row_match_status_enum = Enum(
    RowMatchStatus,
    name="shortlist_row_match_status_enum",
    create_constraint=True,
    validate_strings=True,
)


class ShortlistImport(Base):
    __tablename__ = "shortlist_imports"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    hiring_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("hiring_opportunities.id", ondelete="CASCADE"),
        index=True,
    )
    imported_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
    )
    filename: Mapped[str] = mapped_column(String(255))
    match_field: Mapped[MatchField] = mapped_column(match_field_enum)
    target_status: Mapped[ApplicationStatus] = mapped_column(application_status_enum)
    status: Mapped[ImportStatus] = mapped_column(import_status_enum)
    total_rows: Mapped[int] = mapped_column(Integer, default=0)
    matched_rows: Mapped[int] = mapped_column(Integer, default=0)
    unmatched_rows: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_rows: Mapped[int] = mapped_column(Integer, default=0)
    invalid_rows: Mapped[int] = mapped_column(Integer, default=0)
    rows_updated: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rows_skipped: Mapped[int | None] = mapped_column(Integer, nullable=True)
    imported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rows: Mapped[list["ShortlistImportRow"]] = relationship(
        back_populates="import_record",
        cascade="all, delete-orphan",
    )


class ShortlistImportRow(Base):
    __tablename__ = "shortlist_import_rows"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    import_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("shortlist_imports.id", ondelete="CASCADE"),
        index=True,
    )
    row_number: Mapped[int] = mapped_column(Integer)
    raw_identifier: Mapped[str] = mapped_column(String(255))
    match_status: Mapped[RowMatchStatus] = mapped_column(row_match_status_enum)
    application_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("applications.id", ondelete="SET NULL"),
        nullable=True,
    )
    student_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_status: Mapped[ApplicationStatus | None] = mapped_column(
        application_status_enum,
        nullable=True,
    )
    message: Mapped[str | None] = mapped_column(String(500), nullable=True)

    import_record: Mapped[ShortlistImport] = relationship(back_populates="rows")
