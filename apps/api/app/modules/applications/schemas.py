import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.applications.enums import ApplicationStatus, QuestionType


class ApplicationAnswerInput(BaseModel):
    application_question_id: uuid.UUID
    answer: str = Field(min_length=1)

    @field_validator("answer")
    @classmethod
    def strip_answer(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Answer cannot be empty")
        return stripped


class ApplyRequest(BaseModel):
    selected_resume_id: uuid.UUID
    answers: list[ApplicationAnswerInput] = Field(default_factory=list)


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus
    remarks: str | None = None


class ApplicationAnswerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    application_question_id: uuid.UUID
    answer: str


class ApplicationListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    selected_resume_id: uuid.UUID
    status: ApplicationStatus
    applied_at: datetime
    withdrawn_at: datetime | None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    selected_resume_id: uuid.UUID
    status: ApplicationStatus
    applied_at: datetime
    submitted_by: uuid.UUID
    withdrawn_at: datetime | None
    answers: list[ApplicationAnswerResponse] = Field(default_factory=list)


class ApplicationSnapshotResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    application_id: uuid.UUID
    student_profile_snapshot: dict
    resume_snapshot: dict
    eligibility_snapshot: dict


class ApplicationQuestionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    question: str
    question_type: QuestionType
    is_required: bool
    display_order: int
    choices: list | None = None
