import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.hiring_opportunities.enums import (
    EmploymentType,
    OpportunityDocumentType,
    OpportunityStatus,
    TimelineStage,
    WorkMode,
)
from app.utils.datetime import utc_now

employment_type_enum = Enum(EmploymentType, name="employment_type_enum")
work_mode_enum = Enum(WorkMode, name="work_mode_enum")
opportunity_status_enum = Enum(OpportunityStatus, name="opportunity_status_enum")
opportunity_document_type_enum = Enum(
    OpportunityDocumentType,
    name="opportunity_document_type_enum",
)
timeline_stage_enum = Enum(TimelineStage, name="timeline_stage_enum")


class HiringOpportunity(Base):
    __tablename__ = "hiring_opportunities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("companies.id", ondelete="RESTRICT"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), index=True)
    role: Mapped[str] = mapped_column(String(255))
    employment_type: Mapped[EmploymentType] = mapped_column(employment_type_enum)
    location: Mapped[str] = mapped_column(String(255))
    mode: Mapped[WorkMode] = mapped_column(work_mode_enum)
    ctc_min: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    ctc_max: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    bond_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    job_description: Mapped[str] = mapped_column(Text)
    application_deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[OpportunityStatus] = mapped_column(
        opportunity_status_enum,
        default=OpportunityStatus.DRAFT,
        index=True,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    eligibility_rule: Mapped["EligibilityRule | None"] = relationship(
        back_populates="opportunity",
        cascade="all, delete-orphan",
        uselist=False,
    )
    documents: Mapped[list["OpportunityDocument"]] = relationship(
        back_populates="opportunity",
        cascade="all, delete-orphan",
    )
    timeline_entries: Mapped[list["OpportunityTimeline"]] = relationship(
        back_populates="opportunity",
        cascade="all, delete-orphan",
        order_by="OpportunityTimeline.created_at",
    )


class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    hiring_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("hiring_opportunities.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    minimum_cgpa: Mapped[Decimal | None] = mapped_column(Numeric(4, 2), nullable=True)
    allowed_departments: Mapped[list | None] = mapped_column(JSON, nullable=True)
    allowed_graduation_years: Mapped[list | None] = mapped_column(JSON, nullable=True)
    maximum_active_backlogs: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allow_backlog_history: Mapped[bool] = mapped_column(default=True)
    gender_restriction: Mapped[str | None] = mapped_column(String(20), nullable=True)
    education_requirements: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    opportunity: Mapped[HiringOpportunity] = relationship(
        back_populates="eligibility_rule",
    )


class OpportunityDocument(Base):
    __tablename__ = "opportunity_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    hiring_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("hiring_opportunities.id", ondelete="CASCADE"),
        index=True,
    )
    document_type: Mapped[OpportunityDocumentType] = mapped_column(
        opportunity_document_type_enum,
    )
    file_url: Mapped[str] = mapped_column(String(500))
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    opportunity: Mapped[HiringOpportunity] = relationship(back_populates="documents")


class OpportunityTimeline(Base):
    __tablename__ = "opportunity_timeline"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    hiring_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("hiring_opportunities.id", ondelete="CASCADE"),
        index=True,
    )
    stage: Mapped[TimelineStage] = mapped_column(timeline_stage_enum)
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)

    opportunity: Mapped[HiringOpportunity] = relationship(
        back_populates="timeline_entries",
    )
