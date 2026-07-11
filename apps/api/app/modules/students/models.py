import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.students.enums import (
    DocumentStatus,
    DocumentType,
    EducationType,
    Gender,
    ProfileStatus,
    VerificationStatus,
)
from app.utils.datetime import utc_now

verification_status_enum = Enum(
    VerificationStatus,
    name="verification_status_enum",
    create_constraint=True,
    validate_strings=True,
)

profile_status_enum = Enum(ProfileStatus, name="profile_status_enum")
document_status_enum = Enum(DocumentStatus, name="document_status_enum")
education_type_enum = Enum(EducationType, name="education_type_enum")
gender_enum = Enum(Gender, name="gender_enum")
document_type_enum = Enum(DocumentType, name="document_type_enum")


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(150), unique=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
    )
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student_profiles: Mapped[list["StudentProfile"]] = relationship(
        back_populates="department",
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    department_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("departments.id", ondelete="RESTRICT"),
        index=True,
    )
    roll_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    registration_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    graduation_year: Mapped[int] = mapped_column(Integer)
    profile_status: Mapped[ProfileStatus] = mapped_column(
        profile_status_enum,
        default=ProfileStatus.DRAFT,
    )
    profile_completion: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )

    department: Mapped[Department] = relationship(back_populates="student_profiles")
    personal_information: Mapped["StudentPersonalInformation | None"] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
        uselist=False,
    )
    academic_information: Mapped["StudentAcademicInformation | None"] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
        uselist=False,
    )
    education_history: Mapped[list["StudentEducationHistory"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
    )
    resumes: Mapped[list["StudentResumeLibrary"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["StudentDocument"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
    )
    skills: Mapped[list["StudentSkill"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list["StudentProject"]] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
    )
    verification: Mapped["StudentVerification | None"] = relationship(
        back_populates="student_profile",
        cascade="all, delete-orphan",
        uselist=False,
    )


class StudentPersonalInformation(Base):
    __tablename__ = "student_personal_information"

    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    gender: Mapped[Gender] = mapped_column(gender_enum)
    date_of_birth: Mapped[date] = mapped_column(Date)
    phone_number: Mapped[str] = mapped_column(String(20))
    alternate_phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    personal_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    country: Mapped[str] = mapped_column(String(100))
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    student_profile: Mapped[StudentProfile] = relationship(
        back_populates="personal_information",
    )


class StudentAcademicInformation(Base):
    __tablename__ = "student_academic_information"

    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    current_cgpa: Mapped[Decimal] = mapped_column(Numeric(4, 2))
    active_backlogs: Mapped[int] = mapped_column(Integer, default=0)
    total_history_backlogs: Mapped[int] = mapped_column(Integer, default=0)
    semester: Mapped[int] = mapped_column(Integer)

    student_profile: Mapped[StudentProfile] = relationship(
        back_populates="academic_information",
    )


class StudentEducationHistory(Base):
    __tablename__ = "student_education_history"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        index=True,
    )
    education_type: Mapped[EducationType] = mapped_column(education_type_enum)
    institution: Mapped[str] = mapped_column(String(255))
    board: Mapped[str] = mapped_column(String(255))
    passing_year: Mapped[int] = mapped_column(Integer)
    percentage_or_cgpa: Mapped[str] = mapped_column(String(20))

    student_profile: Mapped[StudentProfile] = relationship(
        back_populates="education_history",
    )


class StudentResumeLibrary(Base):
    __tablename__ = "student_resume_library"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(150))
    file_url: Mapped[str] = mapped_column(String(500))
    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    last_used: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    student_profile: Mapped[StudentProfile] = relationship(back_populates="resumes")


class StudentDocument(Base):
    __tablename__ = "student_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        index=True,
    )
    document_type: Mapped[DocumentType] = mapped_column(document_type_enum)
    file_url: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    status: Mapped[DocumentStatus] = mapped_column(
        document_status_enum,
        default=DocumentStatus.PENDING,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )

    student_profile: Mapped[StudentProfile] = relationship(back_populates="documents")


class StudentSkill(Base):
    __tablename__ = "student_skills"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        index=True,
    )
    skill_name: Mapped[str] = mapped_column(String(100))
    skill_level: Mapped[str] = mapped_column(String(50))

    student_profile: Mapped[StudentProfile] = relationship(back_populates="skills")


class StudentProject(Base):
    __tablename__ = "student_projects"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        index=True,
    )
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    tech_stack: Mapped[str] = mapped_column(String(500))
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    student_profile: Mapped[StudentProfile] = relationship(back_populates="projects")


class StudentVerification(Base):
    __tablename__ = "student_verification"

    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="CASCADE"),
        primary_key=True,
    )
    personal_status: Mapped[VerificationStatus] = mapped_column(
        verification_status_enum,
        default=VerificationStatus.PENDING,
    )
    academic_status: Mapped[VerificationStatus] = mapped_column(
        verification_status_enum,
        default=VerificationStatus.PENDING,
    )
    documents_status: Mapped[VerificationStatus] = mapped_column(
        verification_status_enum,
        default=VerificationStatus.PENDING,
    )
    resume_status: Mapped[VerificationStatus] = mapped_column(
        verification_status_enum,
        default=VerificationStatus.PENDING,
    )
    overall_status: Mapped[VerificationStatus] = mapped_column(
        verification_status_enum,
        default=VerificationStatus.PENDING,
    )
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student_profile: Mapped[StudentProfile] = relationship(
        back_populates="verification",
    )
