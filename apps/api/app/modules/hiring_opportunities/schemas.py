import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.modules.hiring_opportunities.enums import (
    EmploymentType,
    OpportunityDocumentType,
    OpportunityStatus,
    TimelineStage,
    WorkMode,
)


class OpportunityCreate(BaseModel):
    company_id: uuid.UUID
    title: str = Field(min_length=1, max_length=255)
    role: str = Field(min_length=1, max_length=255)
    employment_type: EmploymentType
    location: str = Field(min_length=1, max_length=255)
    mode: WorkMode
    ctc_min: Decimal | None = Field(default=None, ge=0)
    ctc_max: Decimal | None = Field(default=None, ge=0)
    bond_details: str | None = None
    job_description: str = Field(min_length=1)
    application_deadline: datetime

    @field_validator("title", "role")
    @classmethod
    def strip_required(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value cannot be empty")
        return stripped

    @model_validator(mode="after")
    def validate_ctc_range(self) -> "OpportunityCreate":
        if self.ctc_min is not None and self.ctc_max is not None:
            if self.ctc_max < self.ctc_min:
                raise ValueError("ctc_max must be greater than or equal to ctc_min")
        return self


class OpportunityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    role: str | None = Field(default=None, min_length=1, max_length=255)
    employment_type: EmploymentType | None = None
    location: str | None = Field(default=None, min_length=1, max_length=255)
    mode: WorkMode | None = None
    ctc_min: Decimal | None = Field(default=None, ge=0)
    ctc_max: Decimal | None = Field(default=None, ge=0)
    bond_details: str | None = None
    job_description: str | None = Field(default=None, min_length=1)
    application_deadline: datetime | None = None

    @model_validator(mode="after")
    def validate_ctc_range(self) -> "OpportunityUpdate":
        if self.ctc_min is not None and self.ctc_max is not None:
            if self.ctc_max < self.ctc_min:
                raise ValueError("ctc_max must be greater than or equal to ctc_min")
        return self


class OpportunityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    role: str
    employment_type: EmploymentType
    location: str
    mode: WorkMode
    ctc_min: Decimal | None
    ctc_max: Decimal | None
    bond_details: str | None
    job_description: str
    application_deadline: datetime
    status: OpportunityStatus
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    current_timeline_stage: TimelineStage | None = None


class OpportunityListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    title: str
    role: str
    employment_type: EmploymentType
    location: str
    mode: WorkMode
    application_deadline: datetime
    status: OpportunityStatus
    created_at: datetime
    current_timeline_stage: TimelineStage | None = None


class EligibilityRuleUpdate(BaseModel):
    minimum_cgpa: Decimal | None = Field(default=None, ge=0, le=10)
    allowed_departments: list[uuid.UUID] | None = None
    allowed_graduation_years: list[int] | None = None
    maximum_active_backlogs: int | None = Field(default=None, ge=0)
    allow_backlog_history: bool | None = None
    gender_restriction: str | None = Field(default=None, max_length=20)
    education_requirements: dict | None = None

    @field_validator("allowed_graduation_years")
    @classmethod
    def validate_graduation_years(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return value
        for year in value:
            if year < 2000 or year > 2100:
                raise ValueError("Graduation years must be between 2000 and 2100")
        return value


class EligibilityRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    minimum_cgpa: Decimal | None
    allowed_departments: list | None
    allowed_graduation_years: list | None
    maximum_active_backlogs: int | None
    allow_backlog_history: bool
    gender_restriction: str | None
    education_requirements: dict | None


class OpportunityDocumentCreate(BaseModel):
    document_type: OpportunityDocumentType
    file_url: str = Field(min_length=1, max_length=500)


class OpportunityDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    document_type: OpportunityDocumentType
    file_url: str
    uploaded_by: uuid.UUID
    uploaded_at: datetime


class TimelineUpdate(BaseModel):
    stage: TimelineStage
    remarks: str | None = None


class TimelineEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    stage: TimelineStage
    created_by: uuid.UUID
    created_at: datetime
    remarks: str | None
