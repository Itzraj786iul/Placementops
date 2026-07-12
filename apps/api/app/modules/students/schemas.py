import uuid
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.modules.students.enums import (
    DocumentStatus,
    DocumentType,
    EducationType,
    Gender,
    ProfileStatus,
    VerificationStatus,
)

PROFILE_COMPLETION_WEIGHTS = {
    "core": 15,
    "personal": 20,
    "academic": 15,
    "education": 15,
    "resume": 10,
    "documents": 15,
    "skills": 5,
    "projects": 5,
}


class MissingRequirementItem(BaseModel):
    code: str
    label: str
    step: str
    focus: str | None = None
    estimated_minutes: int = 1


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    code: str


class StudentProfileCreate(BaseModel):
    department_id: uuid.UUID
    roll_number: str = Field(min_length=1, max_length=50)
    registration_number: str = Field(min_length=1, max_length=50)
    graduation_year: int = Field(ge=2000, le=2100)

    @field_validator("roll_number", "registration_number")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("Value cannot be empty")
        return stripped


class StudentProfileUpdate(BaseModel):
    department_id: uuid.UUID | None = None
    roll_number: str | None = Field(default=None, min_length=1, max_length=50)
    registration_number: str | None = Field(default=None, min_length=1, max_length=50)
    graduation_year: int | None = Field(default=None, ge=2000, le=2100)
    profile_status: ProfileStatus | None = None


class StudentProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    department_id: uuid.UUID
    roll_number: str
    registration_number: str
    graduation_year: int
    profile_status: ProfileStatus
    profile_completion: int
    missing_requirements: list[MissingRequirementItem] = Field(default_factory=list)
    requirements_completed: int = 0
    requirements_total: int = 0
    optional_completed: int = 0
    optional_total: int = 0
    optional_missing: list[MissingRequirementItem] = Field(default_factory=list)
    estimated_minutes_remaining: int = 0
    created_at: datetime
    updated_at: datetime
    department: DepartmentResponse | None = None


class PersonalInformationCreate(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    gender: Gender
    date_of_birth: date
    phone_number: str = Field(min_length=10, max_length=20)
    alternate_phone: str | None = Field(default=None, max_length=20)
    personal_email: EmailStr | None = None
    address: str = Field(min_length=1)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    country: str = Field(min_length=1, max_length=100)
    photo_url: str | None = Field(default=None, max_length=500)


class PersonalInformationUpdate(PersonalInformationCreate):
    pass


class PersonalInformationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_profile_id: uuid.UUID
    first_name: str
    last_name: str
    gender: Gender
    date_of_birth: date
    phone_number: str
    alternate_phone: str | None
    personal_email: EmailStr | None
    address: str
    city: str
    state: str
    country: str
    photo_url: str | None


class ProfilePhotoUploadResponse(BaseModel):
    photo_url: str


class AcademicInformationCreate(BaseModel):
    current_cgpa: Decimal = Field(ge=0, le=10)
    active_backlogs: int = Field(ge=0)
    total_history_backlogs: int = Field(ge=0)
    semester: int = Field(ge=1, le=12)


class AcademicInformationUpdate(AcademicInformationCreate):
    pass


class AcademicInformationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_profile_id: uuid.UUID
    current_cgpa: Decimal
    active_backlogs: int
    total_history_backlogs: int
    semester: int


class EducationHistoryCreate(BaseModel):
    education_type: EducationType
    institution: str = Field(min_length=1, max_length=255)
    board: str = Field(min_length=1, max_length=255)
    passing_year: int = Field(ge=1980, le=2100)
    percentage_or_cgpa: str = Field(min_length=1, max_length=20)


class EducationHistoryUpdate(EducationHistoryCreate):
    pass


class EducationHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    education_type: EducationType
    institution: str
    board: str
    passing_year: int
    percentage_or_cgpa: str


class ResumeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    file_url: str = Field(min_length=1, max_length=500)
    version: int = Field(ge=1, default=1)
    is_active: bool = False


class ResumeUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    file_url: str | None = Field(default=None, min_length=1, max_length=500)
    version: int | None = Field(default=None, ge=1)
    is_active: bool | None = None


class ResumeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    name: str
    file_url: str
    version: int
    is_active: bool
    last_used: datetime | None
    uploaded_at: datetime


class DocumentCreate(BaseModel):
    document_type: DocumentType
    file_url: str = Field(min_length=1, max_length=500)
    file_name: str = Field(min_length=1, max_length=255)


class DocumentUpdate(BaseModel):
    file_url: str | None = Field(default=None, min_length=1, max_length=500)
    file_name: str | None = Field(default=None, min_length=1, max_length=255)
    status: DocumentStatus | None = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    document_type: DocumentType
    file_url: str
    file_name: str
    status: DocumentStatus
    uploaded_at: datetime


class SkillCreate(BaseModel):
    skill_name: str = Field(min_length=1, max_length=100)
    skill_level: str = Field(min_length=1, max_length=50)


class SkillUpdate(SkillCreate):
    pass


class SkillResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    skill_name: str
    skill_level: str


class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1)
    tech_stack: str = Field(min_length=1, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    demo_url: str | None = Field(default=None, max_length=500)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1)
    tech_stack: str | None = Field(default=None, min_length=1, max_length=500)
    github_url: str | None = Field(default=None, max_length=500)
    demo_url: str | None = Field(default=None, max_length=500)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    student_profile_id: uuid.UUID
    title: str
    description: str
    tech_stack: str
    github_url: str | None
    demo_url: str | None


class VerificationUpdate(BaseModel):
    personal_status: VerificationStatus | None = None
    academic_status: VerificationStatus | None = None
    documents_status: VerificationStatus | None = None
    resume_status: VerificationStatus | None = None
    overall_status: VerificationStatus | None = None
    remarks: str | None = None


class VerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    student_profile_id: uuid.UUID
    personal_status: VerificationStatus
    academic_status: VerificationStatus
    documents_status: VerificationStatus
    resume_status: VerificationStatus
    overall_status: VerificationStatus
    reviewer_id: uuid.UUID | None
    remarks: str | None
    reviewed_at: datetime | None
