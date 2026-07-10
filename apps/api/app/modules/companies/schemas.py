import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.companies.enums import (
    CommunicationType,
    CompanyDocumentType,
    CompanyStatus,
    OwnershipType,
    PipelineStage,
)


class HandlerAssignment(BaseModel):
    handler_user_id: uuid.UUID
    branch: str | None = Field(default=None, max_length=100)
    ownership_type: OwnershipType


class CompanyCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=500)
    linkedin: str | None = Field(default=None, max_length=500)
    headquarters: str | None = Field(default=None, max_length=255)
    company_type: str | None = Field(default=None, max_length=100)
    handler: HandlerAssignment | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Company name cannot be empty")
        return stripped


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    industry: str | None = Field(default=None, max_length=150)
    website: str | None = Field(default=None, max_length=500)
    linkedin: str | None = Field(default=None, max_length=500)
    headquarters: str | None = Field(default=None, max_length=255)
    company_type: str | None = Field(default=None, max_length=100)
    status: CompanyStatus | None = None
    handler: HandlerAssignment | None = None


class CompanyHandlerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    handler_user_id: uuid.UUID
    branch: str | None
    ownership_type: OwnershipType
    assigned_by: uuid.UUID
    assigned_at: datetime
    ended_at: datetime | None
    is_active: bool


class CompanyPipelineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    current_stage: PipelineStage
    last_updated: datetime
    updated_by: uuid.UUID


class CompanyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    industry: str | None
    website: str | None
    linkedin: str | None
    headquarters: str | None
    company_type: str | None
    status: CompanyStatus
    created_by: uuid.UUID
    created_at: datetime
    updated_at: datetime
    pipeline: CompanyPipelineResponse | None = None
    active_handler: CompanyHandlerResponse | None = None


class CompanyListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    industry: str | None
    company_type: str | None
    status: CompanyStatus
    created_at: datetime
    pipeline: CompanyPipelineResponse | None = None
    active_handler: CompanyHandlerResponse | None = None


class CompanyContactCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    designation: str | None = Field(default=None, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=20)
    linkedin: str | None = Field(default=None, max_length=500)
    is_primary: bool = False
    notes: str | None = None


class CompanyContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    name: str
    designation: str | None
    email: str | None
    phone: str | None
    linkedin: str | None
    is_primary: bool
    notes: str | None


class PipelineUpdate(BaseModel):
    current_stage: PipelineStage


class CommunicationCreate(BaseModel):
    type: CommunicationType
    subject: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=1)
    communication_date: datetime


class CommunicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    type: CommunicationType
    subject: str | None
    description: str
    communication_date: datetime
    created_by: uuid.UUID
    created_at: datetime


class DocumentCreate(BaseModel):
    document_type: CompanyDocumentType
    file_url: str = Field(min_length=1, max_length=500)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID
    document_type: CompanyDocumentType
    file_url: str
    uploaded_by: uuid.UUID
    uploaded_at: datetime


class TimelineEntry(BaseModel):
    id: uuid.UUID
    type: CommunicationType
    subject: str | None
    description: str
    communication_date: datetime
    created_by: uuid.UUID
    created_at: datetime
