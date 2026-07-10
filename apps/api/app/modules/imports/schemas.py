import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.applications.enums import ApplicationStatus
from app.modules.imports.enums import ImportStatus, MatchField, RowMatchStatus


class ImportRowPreview(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    row_number: int
    raw_identifier: str
    match_status: RowMatchStatus
    application_id: uuid.UUID | None = None
    student_name: str | None = None
    current_status: ApplicationStatus | None = None
    message: str | None = None


class ImportPreviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    imported_by: uuid.UUID
    filename: str
    match_field: MatchField
    target_status: ApplicationStatus
    status: ImportStatus
    total_rows: int
    matched_rows: int
    unmatched_rows: int
    duplicate_rows: int
    invalid_rows: int
    rows_updated: int | None = None
    rows_skipped: int | None = None
    imported_at: datetime
    confirmed_at: datetime | None = None
    rows: list[ImportRowPreview] = Field(default_factory=list)


class ImportConfirmResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    status: ImportStatus
    target_status: ApplicationStatus
    imported_by: uuid.UUID
    imported_at: datetime
    confirmed_at: datetime | None = None
    rows_updated: int
    rows_skipped: int
    matched_rows: int
    unmatched_rows: int
    duplicate_rows: int
    invalid_rows: int
