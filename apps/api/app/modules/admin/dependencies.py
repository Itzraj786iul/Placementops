from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.modules.admin.org_service import AdminOrgService
from app.modules.admin.service import AdminUserService
from app.modules.admin.settings_service import AdminSettingsService
from app.modules.admin.health_service import AdminHealthService
from app.modules.admin.feature_flag_service import FeatureFlagService
from app.modules.admin.maintenance_service import MaintenanceService


def get_admin_user_service(
    db: Session = Depends(get_db_session),
) -> AdminUserService:
    return AdminUserService(db)


def get_admin_org_service(
    db: Session = Depends(get_db_session),
) -> AdminOrgService:
    return AdminOrgService(db)


def get_admin_settings_service(
    db: Session = Depends(get_db_session),
) -> AdminSettingsService:
    return AdminSettingsService(db)


def get_admin_health_service(
    db: Session = Depends(get_db_session),
) -> AdminHealthService:
    return AdminHealthService(db)


def get_feature_flag_service(
    db: Session = Depends(get_db_session),
) -> FeatureFlagService:
    return FeatureFlagService(db)


def get_maintenance_service(
    db: Session = Depends(get_db_session),
) -> MaintenanceService:
    return MaintenanceService(db)
