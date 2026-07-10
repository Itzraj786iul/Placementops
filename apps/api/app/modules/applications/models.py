import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.modules.applications.enums import ApplicationStatus, QuestionType
from app.utils.datetime import utc_now

application_status_enum = Enum(ApplicationStatus, name="application_status_enum")
question_type_enum = Enum(QuestionType, name="question_type_enum")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint(
            "student_profile_id",
            "hiring_opportunity_id",
            name="uq_applications_student_opportunity",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    student_profile_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_profiles.id", ondelete="RESTRICT"),
        index=True,
    )
    hiring_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("hiring_opportunities.id", ondelete="RESTRICT"),
        index=True,
    )
    selected_resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("student_resume_library.id", ondelete="RESTRICT"),
        index=True,
    )
    status: Mapped[ApplicationStatus] = mapped_column(
        application_status_enum,
        default=ApplicationStatus.APPLIED,
        index=True,
    )
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
    )
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("users.id", ondelete="RESTRICT"),
        index=True,
    )
    withdrawn_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    student_profile: Mapped["StudentProfile"] = relationship(
        "StudentProfile",
        foreign_keys=[student_profile_id],
    )
    hiring_opportunity: Mapped["HiringOpportunity"] = relationship(
        "HiringOpportunity",
        foreign_keys=[hiring_opportunity_id],
    )
    selected_resume: Mapped["StudentResumeLibrary"] = relationship(
        "StudentResumeLibrary",
        foreign_keys=[selected_resume_id],
    )
    snapshot: Mapped["ApplicationSnapshot | None"] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
        uselist=False,
    )
    answers: Mapped[list["ApplicationAnswer"]] = relationship(
        back_populates="application",
        cascade="all, delete-orphan",
    )


class ApplicationSnapshot(Base):
    __tablename__ = "application_snapshots"

    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("applications.id", ondelete="CASCADE"),
        primary_key=True,
    )
    student_profile_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    resume_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    eligibility_snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)

    application: Mapped[Application] = relationship(back_populates="snapshot")


class ApplicationQuestion(Base):
    __tablename__ = "application_questions"

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
    question: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(question_type_enum)
    is_required: Mapped[bool] = mapped_column(default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    choices: Mapped[list | None] = mapped_column(JSON, nullable=True)

    hiring_opportunity: Mapped["HiringOpportunity"] = relationship(
        "HiringOpportunity",
        foreign_keys=[hiring_opportunity_id],
    )
    answers: Mapped[list["ApplicationAnswer"]] = relationship(
        back_populates="question",
    )


class ApplicationAnswer(Base):
    __tablename__ = "application_answers"
    __table_args__ = (
        UniqueConstraint(
            "application_id",
            "application_question_id",
            name="uq_application_answers_application_question",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("applications.id", ondelete="CASCADE"),
        index=True,
    )
    application_question_id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        ForeignKey("application_questions.id", ondelete="RESTRICT"),
        index=True,
    )
    answer: Mapped[str] = mapped_column(Text, nullable=False)

    application: Mapped[Application] = relationship(back_populates="answers")
    question: Mapped[ApplicationQuestion] = relationship(back_populates="answers")
