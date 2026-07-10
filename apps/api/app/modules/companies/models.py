import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.companies.enums import (
    CommunicationType,
    CompanyDocumentType,
    CompanyStatus,
    OwnershipType,
    PipelineStage,
)
from app.utils.datetime import utc_now

company_status_enum = Enum(CompanyStatus, name="company_status_enum")
ownership_type_enum = Enum(OwnershipType, name="ownership_type_enum")
pipeline_stage_enum = Enum(PipelineStage, name="pipeline_stage_enum")
communication_type_enum = Enum(CommunicationType, name="communication_type_enum")
company_document_type_enum = Enum(CompanyDocumentType, name="company_document_type_enum")


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), index=True)
    industry: Mapped[str | None] = mapped_column(String(150), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(500), nullable=True)
    headquarters: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[CompanyStatus] = mapped_column(
        company_status_enum,
        default=CompanyStatus.ACTIVE,
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

    contacts: Mapped[list["CompanyContact"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    handlers: Mapped[list["CompanyHandler"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    pipeline: Mapped["CompanyPipeline | None"] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
        uselist=False,
    )
    communications: Mapped[list["CompanyCommunication"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["CompanyDocument"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )


class CompanyContact(Base):
    __tablename__ = "company_contacts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150))
    designation: Mapped[str | None] = mapped_column(String(150), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    company: Mapped[Company] = relationship(back_populates="contacts")


class CompanyHandler(Base):
    __tablename__ = "company_handlers"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
    )
    handler_user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    branch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ownership_type: Mapped[OwnershipType] = mapped_column(ownership_type_enum)
    assigned_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    company: Mapped[Company] = relationship(back_populates="handlers")


class CompanyPipeline(Base):
    __tablename__ = "company_pipeline"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("companies.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    current_stage: Mapped[PipelineStage] = mapped_column(
        pipeline_stage_enum,
        default=PipelineStage.NOT_CONTACTED,
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
    )

    company: Mapped[Company] = relationship(back_populates="pipeline")


class CompanyCommunication(Base):
    __tablename__ = "company_communications"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
    )
    type: Mapped[CommunicationType] = mapped_column(communication_type_enum)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str] = mapped_column(Text)
    communication_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    company: Mapped[Company] = relationship(back_populates="communications")


class CompanyDocument(Base):
    __tablename__ = "company_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("companies.id", ondelete="CASCADE"),
        index=True,
    )
    document_type: Mapped[CompanyDocumentType] = mapped_column(company_document_type_enum)
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

    company: Mapped[Company] = relationship(back_populates="documents")
