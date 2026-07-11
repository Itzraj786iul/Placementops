import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.admin.dependencies import get_admin_user_service
from app.modules.admin.schemas import (
    AdminAuditListResponse,
    AdminBulkResult,
    AdminBulkUpdate,
    AdminRolesUpdate,
    AdminUserDetail,
    AdminUserListResponse,
    AdminUserUpdate,
)
from app.modules.admin.service import AdminUserService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/users", response_model=AdminUserListResponse)
def list_admin_users(
    search: str | None = Query(default=None),
    role: str | None = Query(default=None),
    status: str | None = Query(default=None),
    department_id: uuid.UUID | None = Query(default=None),
    verification: str | None = Query(default=None),
    graduation_year: int | None = Query(default=None),
    sort_by: str = Query(default="created_at"),
    sort_order: str = Query(default="desc"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserListResponse:
    return service.list_users(
        current_user,
        search=search,
        role=role,
        status=status,
        department_id=department_id,
        verification=verification,
        graduation_year=graduation_year,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        page_size=page_size,
    )


@admin_router.patch("/users/bulk", response_model=AdminBulkResult)
def bulk_update_users(
    payload: AdminBulkUpdate,
    current_user: User = Depends(get_current_user),
    service: AdminUserService = Depends(get_admin_user_service),
) -> AdminBulkResult:
    return service.bulk_update(current_user, payload)


@admin_router.get("/users/{user_id}", response_model=AdminUserDetail)
def get_admin_user(
    user_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserDetail:
    return service.get_user(current_user, user_id)


@admin_router.patch("/users/{user_id}", response_model=AdminUserDetail)
def update_admin_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdate,
    current_user: User = Depends(get_current_user),
    service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserDetail:
    return service.update_user(current_user, user_id, payload)


@admin_router.patch("/users/{user_id}/roles", response_model=AdminUserDetail)
def update_admin_user_roles(
    user_id: uuid.UUID,
    payload: AdminRolesUpdate,
    current_user: User = Depends(get_current_user),
    service: AdminUserService = Depends(get_admin_user_service),
) -> AdminUserDetail:
    return service.update_roles(current_user, user_id, payload)


@admin_router.get("/users/{user_id}/audit", response_model=AdminAuditListResponse)
def get_admin_user_audit(
    user_id: uuid.UUID,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: AdminUserService = Depends(get_admin_user_service),
) -> AdminAuditListResponse:
    return service.get_user_audit(
        current_user,
        user_id,
        page=page,
        page_size=page_size,
    )
