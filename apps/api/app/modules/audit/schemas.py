import math
import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.modules.audit.enums import AuditAction, AuditEntityType


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID
    entity_type: AuditEntityType
    entity_id: uuid.UUID
    action: AuditAction
    performed_by: uuid.UUID
    performed_at: datetime
    old_values: dict[str, Any] | None = None
    new_values: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = Field(
        default=None,
        validation_alias="metadata_",
        serialization_alias="metadata",
    )
    ip_address: str | None = None
    user_agent: str | None = None


class AuditListResponse(BaseModel):
    items: list[AuditLogResponse]
    page: int
    page_size: int
    total: int
    total_pages: int


class AuditListQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    entity_type: AuditEntityType | None = None
    action: AuditAction | None = None
    performed_by: uuid.UUID | None = None

    @field_validator("page_size")
    @classmethod
    def clamp_page_size(cls, value: int) -> int:
        return value


def build_list_response(
    items: list[AuditLogResponse],
    *,
    page: int,
    page_size: int,
    total: int,
) -> AuditListResponse:
    total_pages = math.ceil(total / page_size) if page_size and total else 0
    return AuditListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )
