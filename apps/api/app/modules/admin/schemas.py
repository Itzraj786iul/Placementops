import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.models import USER_STATUS_ACTIVE, User
from app.modules.users.schemas import RoleResponse

UserStatus = Literal["active", "inactive", "suspended", "archived"]
SortField = Literal[
    "name",
    "email",
    "status",
    "last_login",
    "created_at",
]
SortOrder = Literal["asc", "desc"]
BulkAction = Literal["activate", "deactivate", "assign_role", "export"]


class AdminUserListItem(BaseModel):
    id: uuid.UUID
    college_email: str
    first_name: str
    last_name: str
    display_name: str
    profile_picture: str | None
    status: str
    is_active: bool
    roles: list[RoleResponse]
    primary_role: str | None
    department_name: str | None
    department_code: str | None
    roll_number: str | None
    registration_number: str | None
    verification_status: str | None
    graduation_year: int | None
    last_login: datetime | None
    created_at: datetime


class AdminUserListResponse(BaseModel):
    items: list[AdminUserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class RoleAssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    role_id: uuid.UUID
    role_name: str
    is_primary: bool


class RoleHistoryItem(BaseModel):
    id: uuid.UUID
    role_name: str
    action: str
    performed_by: uuid.UUID
    is_primary: bool
    created_at: datetime


class AdminUserDetail(BaseModel):
    id: uuid.UUID
    college_email: str
    personal_email: str | None
    first_name: str
    last_name: str
    display_name: str
    profile_picture: str | None
    status: str
    is_active: bool
    email_verified: bool
    roles: list[RoleResponse]
    role_assignments: list[RoleAssignmentResponse]
    primary_role: str | None
    department_name: str | None
    department_code: str | None
    roll_number: str | None
    registration_number: str | None
    graduation_year: int | None
    profile_status: str | None
    verification_status: str | None
    student_profile_id: uuid.UUID | None
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime
    role_history: list[RoleHistoryItem]
    statistics: dict[str, int | str | None]
    current_sessions: list[dict] = Field(default_factory=list)


class AdminUserUpdate(BaseModel):
    status: UserStatus | None = None
    first_name: str | None = Field(default=None, min_length=1, max_length=100)
    last_name: str | None = Field(default=None, min_length=1, max_length=100)
    display_name: str | None = Field(default=None, min_length=1, max_length=200)


class AdminRolesUpdate(BaseModel):
    assign: list[str] = Field(default_factory=list)
    remove: list[str] = Field(default_factory=list)
    primary_role: str | None = None


class AdminBulkUpdate(BaseModel):
    user_ids: list[uuid.UUID] = Field(min_length=1, max_length=200)
    action: BulkAction
    role_name: str | None = None
    confirm: bool = False


class AdminBulkResult(BaseModel):
    updated: int
    skipped: int
    export_rows: list[AdminUserListItem] | None = None


class AdminAuditItem(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: uuid.UUID
    action: str
    performed_by: uuid.UUID
    performed_at: datetime
    old_values: dict | None
    new_values: dict | None
    metadata: dict | None


class AdminAuditListResponse(BaseModel):
    items: list[AdminAuditItem]
    total: int


def user_is_active(user: User) -> bool:
    return user.status == USER_STATUS_ACTIVE
