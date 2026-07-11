import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.admin.dependencies import (
    get_admin_health_service,
    get_admin_org_service,
    get_admin_settings_service,
    get_admin_user_service,
    get_feature_flag_service,
    get_maintenance_service,
)
from app.modules.admin.org_schemas import (
    AdminDepartmentCreate,
    AdminDepartmentListResponse,
    AdminDepartmentResponse,
    AdminDepartmentUpdate,
    AdminSeasonCreate,
    AdminSeasonListResponse,
    AdminSeasonResponse,
    AdminSeasonUpdate,
    SeasonActivateRequest,
)
from app.modules.admin.org_service import AdminOrgService
from app.modules.admin.health_schemas import SystemHealthResponse
from app.modules.admin.health_service import AdminHealthService
from app.modules.admin.feature_flag_schemas import (
    FeatureFlagListResponse,
    FeatureFlagResponse,
    FeatureFlagUpdate,
)
from app.modules.admin.feature_flag_service import FeatureFlagService
from app.modules.admin.maintenance_schemas import (
    MaintenanceAdminResponse,
    MaintenanceUpdate,
)
from app.modules.admin.maintenance_service import MaintenanceService
from app.modules.admin.settings_schemas import (
    AdminSettingsResponse,
    AdminSettingsUpdate,
)
from app.modules.admin.settings_service import AdminSettingsService
from app.modules.admin.schemas import (
    AdminAuditListResponse,
    AdminBulkResult,
    AdminBulkUpdate,
    AdminRolesUpdate,
    AdminUserDetail,
    AdminUserInvite,
    AdminUserListResponse,
    AdminUserUpdate,
)
from app.modules.admin.service import AdminUserService
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse
from app.platform.auth.dependencies import get_auth_service, get_current_user
from app.platform.auth.service import AuthService

admin_router = APIRouter(prefix="/admin", tags=["admin"])


@admin_router.get("/maintenance", response_model=MaintenanceAdminResponse)
def get_admin_maintenance(
    current_user: User = Depends(get_current_user),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceAdminResponse:
    return service.get_admin_status(current_user)


@admin_router.patch("/maintenance", response_model=MaintenanceAdminResponse)
def patch_admin_maintenance(
    payload: MaintenanceUpdate,
    current_user: User = Depends(get_current_user),
    service: MaintenanceService = Depends(get_maintenance_service),
) -> MaintenanceAdminResponse:
    return service.update(current_user, payload)


@admin_router.get("/feature-flags", response_model=FeatureFlagListResponse)
def list_feature_flags(
    search: str | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: FeatureFlagService = Depends(get_feature_flag_service),
) -> FeatureFlagListResponse:
    return service.list_flags(current_user, search=search)


@admin_router.patch(
    "/feature-flags/{key}",
    response_model=FeatureFlagResponse,
)
def patch_feature_flag(
    key: str,
    payload: FeatureFlagUpdate,
    current_user: User = Depends(get_current_user),
    service: FeatureFlagService = Depends(get_feature_flag_service),
) -> FeatureFlagResponse:
    return service.update_flag(current_user, key, payload)


@admin_router.get("/system-health", response_model=SystemHealthResponse)
def get_admin_system_health(
    current_user: User = Depends(get_current_user),
    service: AdminHealthService = Depends(get_admin_health_service),
) -> SystemHealthResponse:
    return service.get_system_health(current_user)


@admin_router.get("/settings", response_model=AdminSettingsResponse)
def get_admin_settings(
    current_user: User = Depends(get_current_user),
    service: AdminSettingsService = Depends(get_admin_settings_service),
) -> AdminSettingsResponse:
    return service.get_settings(current_user)


@admin_router.patch("/settings", response_model=AdminSettingsResponse)
def patch_admin_settings(
    payload: AdminSettingsUpdate,
    current_user: User = Depends(get_current_user),
    service: AdminSettingsService = Depends(get_admin_settings_service),
) -> AdminSettingsResponse:
    return service.update_settings(current_user, payload)


@admin_router.get("/departments", response_model=AdminDepartmentListResponse)
def list_admin_departments(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminDepartmentListResponse:
    return service.list_departments(
        current_user,
        search=search,
        status=status,
        page=page,
        page_size=page_size,
    )


@admin_router.post(
    "/departments",
    response_model=AdminDepartmentResponse,
    status_code=201,
)
def create_admin_department(
    payload: AdminDepartmentCreate,
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminDepartmentResponse:
    return service.create_department(current_user, payload)


@admin_router.patch(
    "/departments/{department_id}",
    response_model=AdminDepartmentResponse,
)
def update_admin_department(
    department_id: uuid.UUID,
    payload: AdminDepartmentUpdate,
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminDepartmentResponse:
    return service.update_department(current_user, department_id, payload)


@admin_router.get("/seasons", response_model=AdminSeasonListResponse)
def list_admin_seasons(
    search: str | None = Query(default=None),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminSeasonListResponse:
    return service.list_seasons(
        current_user,
        search=search,
        status=status,
        page=page,
        page_size=page_size,
    )


@admin_router.post("/seasons", response_model=AdminSeasonResponse, status_code=201)
def create_admin_season(
    payload: AdminSeasonCreate,
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminSeasonResponse:
    return service.create_season(current_user, payload)


@admin_router.patch("/seasons/{season_id}", response_model=AdminSeasonResponse)
def update_admin_season(
    season_id: uuid.UUID,
    payload: AdminSeasonUpdate,
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminSeasonResponse:
    return service.update_season(current_user, season_id, payload)


@admin_router.post(
    "/seasons/{season_id}/activate",
    response_model=AdminSeasonResponse,
)
def activate_admin_season(
    season_id: uuid.UUID,
    payload: SeasonActivateRequest,
    current_user: User = Depends(get_current_user),
    service: AdminOrgService = Depends(get_admin_org_service),
) -> AdminSeasonResponse:
    return service.activate_season(current_user, season_id, payload)


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


@admin_router.post("/users", response_model=UserResponse, status_code=201)
def invite_admin_user(
    payload: AdminUserInvite,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Create a staff/student account and email an activation link."""
    return auth_service.invite_staff_user(
        actor=current_user,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role_name=payload.role,
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
