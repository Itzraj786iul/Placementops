from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.admin.access import ensure_admin_access, is_super_admin
from app.modules.admin.exceptions import (
    AdminForbiddenError,
    AdminNotFoundError,
    AdminValidationError,
)
from app.modules.admin.org_repository import AdminOrgRepository
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
    SeasonStats,
    pages,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.seasons.models import (
    SEASON_STATUS_ACTIVE,
    SEASON_STATUS_ARCHIVED,
    SEASON_STATUS_COMPLETED,
    SEASON_STATUS_PLANNING,
    SEASON_STATUSES,
    PlacementSeason,
)
from app.modules.students.models import Department
from app.modules.users.models import User
from app.utils.datetime import utc_now

class AdminOrgService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminOrgRepository(db)

    # ---- Departments ----

    def list_departments(
        self,
        actor: User,
        *,
        search: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> AdminDepartmentListResponse:
        ensure_admin_access(actor)
        rows, total = self.repository.list_departments(
            search=search,
            status=status,
            page=page,
            page_size=page_size,
        )
        items = [self._department_response(d) for d in rows]
        return AdminDepartmentListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=pages(total, page_size),
        )

    def create_department(
        self,
        actor: User,
        payload: AdminDepartmentCreate,
    ) -> AdminDepartmentResponse:
        ensure_admin_access(actor)
        code = payload.code.strip().upper()
        name = payload.name.strip()
        if self.repository.get_department_by_code(code):
            raise AdminValidationError("Department code must be unique")
        if self.repository.get_department_by_name(name):
            raise AdminValidationError("Department name must be unique")

        department = Department(
            name=name,
            code=code,
            description=payload.description,
            display_order=payload.display_order,
            status="active",
        )
        self.repository.add_department(department)
        record_audit(
            self.db,
            entity_type=AuditEntityType.DEPARTMENT,
            entity_id=department.id,
            action=AuditAction.CREATE,
            performed_by=actor.id,
            new_values={"name": name, "code": code},
        )
        self.db.commit()
        return self._department_response(department)

    def update_department(
        self,
        actor: User,
        department_id: uuid.UUID,
        payload: AdminDepartmentUpdate,
    ) -> AdminDepartmentResponse:
        ensure_admin_access(actor)
        department = self.repository.get_department(department_id)
        if department is None:
            raise AdminNotFoundError("Department not found")

        old: dict = {}
        new: dict = {}

        if payload.name is not None:
            name = payload.name.strip()
            existing = self.repository.get_department_by_name(name)
            if existing and existing.id != department.id:
                raise AdminValidationError("Department name must be unique")
            old["name"] = department.name
            new["name"] = name
            department.name = name

        if payload.code is not None:
            code = payload.code.strip().upper()
            existing = self.repository.get_department_by_code(code)
            if existing and existing.id != department.id:
                raise AdminValidationError("Department code must be unique")
            old["code"] = department.code
            new["code"] = code
            department.code = code

        if payload.description is not None:
            old["description"] = department.description
            new["description"] = payload.description
            department.description = payload.description

        if payload.display_order is not None:
            old["display_order"] = department.display_order
            new["display_order"] = payload.display_order
            department.display_order = payload.display_order

        if payload.logo_url is not None:
            old["logo_url"] = department.logo_url
            new["logo_url"] = payload.logo_url
            department.logo_url = payload.logo_url

        if payload.status is not None:
            old["status"] = department.status
            new["status"] = payload.status
            department.status = payload.status
            if payload.status == "archived":
                department.archived_at = utc_now()
            elif payload.status == "active":
                department.archived_at = None

        department.updated_at = utc_now()
        if new:
            record_audit(
                self.db,
                entity_type=AuditEntityType.DEPARTMENT,
                entity_id=department.id,
                action=AuditAction.UPDATE,
                performed_by=actor.id,
                old_values=old,
                new_values=new,
            )
        self.db.commit()
        return self._department_response(department)

    # ---- Seasons ----

    def list_seasons(
        self,
        actor: User,
        *,
        search: str | None = None,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
        include_stats: bool = True,
    ) -> AdminSeasonListResponse:
        ensure_admin_access(actor)
        rows, total = self.repository.list_seasons(
            search=search,
            status=status,
            page=page,
            page_size=page_size,
        )
        items = [
            self._season_response(s, include_stats=include_stats) for s in rows
        ]
        return AdminSeasonListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=pages(total, page_size),
        )

    def create_season(
        self,
        actor: User,
        payload: AdminSeasonCreate,
    ) -> AdminSeasonResponse:
        ensure_admin_access(actor)
        if payload.end_date < payload.start_date:
            raise AdminValidationError("end_date must be on or after start_date")
        if payload.status not in SEASON_STATUSES:
            raise AdminValidationError("Invalid season status")
        if payload.status == SEASON_STATUS_ACTIVE:
            raise AdminValidationError(
                "Create as planning, then activate with confirmation",
            )

        season = PlacementSeason(
            name=payload.name.strip(),
            academic_batch=payload.academic_batch.strip(),
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=payload.status or SEASON_STATUS_PLANNING,
            description=payload.description,
            is_current=False,
        )
        self.repository.add_season(season)
        record_audit(
            self.db,
            entity_type=AuditEntityType.PLACEMENT_SEASON,
            entity_id=season.id,
            action=AuditAction.CREATE,
            performed_by=actor.id,
            new_values={
                "name": season.name,
                "academic_batch": season.academic_batch,
                "status": season.status,
            },
        )
        self.db.commit()
        return self._season_response(season)

    def update_season(
        self,
        actor: User,
        season_id: uuid.UUID,
        payload: AdminSeasonUpdate,
    ) -> AdminSeasonResponse:
        ensure_admin_access(actor)
        season = self.repository.get_season(season_id)
        if season is None:
            raise AdminNotFoundError("Season not found")

        if season.status == SEASON_STATUS_COMPLETED:
            # Allow only archive transition from completed
            if payload.status != SEASON_STATUS_ARCHIVED and any(
                v is not None
                for k, v in payload.model_dump().items()
                if k != "status" and v is not None
            ):
                raise AdminValidationError("Completed seasons are read-only")
            if payload.status is None:
                raise AdminValidationError("Completed seasons are read-only")

        if payload.status == SEASON_STATUS_ACTIVE:
            raise AdminValidationError(
                "Use POST /admin/seasons/{id}/activate to make a season active",
            )

        # Placement Cell cannot hard-delete; archive is allowed
        if (
            payload.status == SEASON_STATUS_ARCHIVED
            and not is_super_admin(actor)
            and season.status == SEASON_STATUS_ACTIVE
        ):
            raise AdminForbiddenError(
                "Only SUPER_ADMIN can archive the active season",
            )

        old: dict = {}
        new: dict = {}

        if payload.name is not None:
            old["name"] = season.name
            new["name"] = payload.name.strip()
            season.name = payload.name.strip()
        if payload.academic_batch is not None:
            old["academic_batch"] = season.academic_batch
            new["academic_batch"] = payload.academic_batch.strip()
            season.academic_batch = payload.academic_batch.strip()
        if payload.start_date is not None:
            old["start_date"] = str(season.start_date)
            new["start_date"] = str(payload.start_date)
            season.start_date = payload.start_date
        if payload.end_date is not None:
            old["end_date"] = str(season.end_date)
            new["end_date"] = str(payload.end_date)
            season.end_date = payload.end_date
        if payload.description is not None:
            old["description"] = season.description
            new["description"] = payload.description
            season.description = payload.description
        if payload.status is not None:
            if payload.status not in SEASON_STATUSES:
                raise AdminValidationError("Invalid season status")
            old["status"] = season.status
            new["status"] = payload.status
            season.status = payload.status
            if payload.status != SEASON_STATUS_ACTIVE:
                season.is_current = False

        if season.end_date < season.start_date:
            raise AdminValidationError("end_date must be on or after start_date")

        season.updated_at = utc_now()
        if new:
            record_audit(
                self.db,
                entity_type=AuditEntityType.PLACEMENT_SEASON,
                entity_id=season.id,
                action=AuditAction.UPDATE,
                performed_by=actor.id,
                old_values=old,
                new_values=new,
            )
        self.db.commit()
        return self._season_response(season)

    def activate_season(
        self,
        actor: User,
        season_id: uuid.UUID,
        payload: SeasonActivateRequest,
    ) -> AdminSeasonResponse:
        ensure_admin_access(actor)
        if not payload.confirm:
            raise AdminValidationError(
                "Activating a season requires confirm=true",
            )
        season = self.repository.get_season(season_id)
        if season is None:
            raise AdminNotFoundError("Season not found")
        if season.status == SEASON_STATUS_ARCHIVED:
            raise AdminValidationError("Cannot activate an archived season")

        self.repository.clear_current_active()
        season.status = SEASON_STATUS_ACTIVE
        season.is_current = True
        season.updated_at = utc_now()
        record_audit(
            self.db,
            entity_type=AuditEntityType.PLACEMENT_SEASON,
            entity_id=season.id,
            action=AuditAction.UPDATE,
            performed_by=actor.id,
            new_values={"status": SEASON_STATUS_ACTIVE, "is_current": True},
            metadata={"action": "activate"},
        )
        self.db.commit()
        return self._season_response(season)

    def _department_response(self, department: Department) -> AdminDepartmentResponse:
        counts = self.repository.department_counts(department.id)
        return AdminDepartmentResponse(
            id=department.id,
            name=department.name,
            code=department.code,
            description=department.description,
            display_order=department.display_order,
            status=department.status,
            logo_url=department.logo_url,
            created_at=department.created_at,
            updated_at=department.updated_at,
            archived_at=department.archived_at,
            student_count=counts.student_count,
            convener_count=counts.convener_count,
            company_count=counts.company_count,
        )

    def _season_response(
        self,
        season: PlacementSeason,
        *,
        include_stats: bool = True,
    ) -> AdminSeasonResponse:
        stats = None
        if include_stats:
            raw = self.repository.season_stats(season.id)
            stats = SeasonStats(**raw)
        return AdminSeasonResponse(
            id=season.id,
            name=season.name,
            academic_batch=season.academic_batch,
            start_date=season.start_date,
            end_date=season.end_date,
            status=season.status,
            is_current=season.is_current,
            description=season.description,
            created_at=season.created_at,
            updated_at=season.updated_at,
            read_only=season.status == SEASON_STATUS_COMPLETED,
            stats=stats,
        )
