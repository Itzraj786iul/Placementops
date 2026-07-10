import uuid

from pydantic import BaseModel, Field, field_validator

from app.modules.applications.enums import ApplicationStatus
from app.modules.exports.enums import (
    DEFAULT_COLUMNS,
    ExportColumn,
    ExportFormat,
    ExportScope,
)


class ExportFilters(BaseModel):
    status: list[ApplicationStatus] | None = None
    department: str | None = None
    company_id: uuid.UUID | None = None


class ExportRequest(BaseModel):
    format: ExportFormat = ExportFormat.XLSX
    scope: ExportScope = ExportScope.ALL
    columns: list[ExportColumn] = Field(default_factory=lambda: list(DEFAULT_COLUMNS))
    filters: ExportFilters = Field(default_factory=ExportFilters)

    @field_validator("columns")
    @classmethod
    def require_columns(cls, value: list[ExportColumn]) -> list[ExportColumn]:
        if not value:
            raise ValueError("At least one column must be selected")
        # Preserve order, drop duplicates
        seen: set[ExportColumn] = set()
        unique: list[ExportColumn] = []
        for column in value:
            if column not in seen:
                seen.add(column)
                unique.append(column)
        return unique
