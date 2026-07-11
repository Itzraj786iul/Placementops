import math
import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, Field

DepartmentStatus = Literal["active", "archived"]
SeasonStatus = Literal["planning", "active", "completed", "archived"]


class AdminDepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str
    code: str
    description: str | None
    display_order: int
    status: str
    logo_url: str | None
    created_at: datetime
    updated_at: datetime
    archived_at: datetime | None
    student_count: int
    convener_count: int
    company_count: int


class AdminDepartmentListResponse(BaseModel):
    items: list[AdminDepartmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminDepartmentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    code: str = Field(min_length=1, max_length=20)
    description: str | None = None
    display_order: int = 0


class AdminDepartmentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    code: str | None = Field(default=None, min_length=1, max_length=20)
    description: str | None = None
    display_order: int | None = None
    status: DepartmentStatus | None = None
    logo_url: str | None = None


class SeasonStats(BaseModel):
    applications: int
    companies: int
    students: int
    offers: int


class AdminSeasonResponse(BaseModel):
    id: uuid.UUID
    name: str
    academic_batch: str
    start_date: date
    end_date: date
    status: str
    is_current: bool
    description: str | None
    created_at: datetime
    updated_at: datetime
    read_only: bool
    stats: SeasonStats | None = None


class AdminSeasonListResponse(BaseModel):
    items: list[AdminSeasonResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminSeasonCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    academic_batch: str = Field(min_length=1, max_length=50)
    start_date: date
    end_date: date
    status: SeasonStatus = "planning"
    description: str | None = None


class AdminSeasonUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    academic_batch: str | None = Field(default=None, min_length=1, max_length=50)
    start_date: date | None = None
    end_date: date | None = None
    status: SeasonStatus | None = None
    description: str | None = None


class SeasonActivateRequest(BaseModel):
    confirm: bool = False


def pages(total: int, page_size: int) -> int:
    if page_size <= 0:
        return 0
    return max(1, math.ceil(total / page_size)) if total else 0
