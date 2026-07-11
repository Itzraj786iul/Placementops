from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.modules.applications.enums import ApplicationStatus
from app.modules.applications.models import Application
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.seasons.models import PlacementSeason
from app.modules.students.models import Department, StudentProfile
from app.modules.users.models import Role, User, UserRole
from app.utils.datetime import utc_now


@dataclass
class DepartmentCounts:
    student_count: int
    convener_count: int
    company_count: int


class AdminOrgRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- Departments ----

    def list_departments(
        self,
        *,
        search: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Department], int]:
        stmt = select(Department)
        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Department.name).like(term),
                    func.lower(Department.code).like(term),
                ),
            )
        if status:
            stmt = stmt.where(Department.status == status)

        total = int(
            self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0,
        )
        rows = list(
            self.db.scalars(
                stmt.order_by(Department.display_order.asc(), Department.name.asc())
                .offset((page - 1) * page_size)
                .limit(page_size),
            ).all(),
        )
        return rows, total

    def get_department(self, department_id: uuid.UUID) -> Department | None:
        return self.db.get(Department, department_id)

    def get_department_by_code(self, code: str) -> Department | None:
        return self.db.scalars(
            select(Department).where(func.lower(Department.code) == code.lower()),
        ).first()

    def get_department_by_name(self, name: str) -> Department | None:
        return self.db.scalars(
            select(Department).where(func.lower(Department.name) == name.lower()),
        ).first()

    def add_department(self, department: Department) -> Department:
        self.db.add(department)
        self.db.flush()
        return department

    def department_counts(self, department_id: uuid.UUID) -> DepartmentCounts:
        student_count = int(
            self.db.scalar(
                select(func.count())
                .select_from(StudentProfile)
                .where(StudentProfile.department_id == department_id),
            )
            or 0,
        )
        convener_count = int(
            self.db.scalar(
                select(func.count(func.distinct(User.id)))
                .select_from(User)
                .join(UserRole, UserRole.user_id == User.id)
                .join(Role, Role.id == UserRole.role_id)
                .join(StudentProfile, StudentProfile.user_id == User.id)
                .where(
                    Role.name == "PLACEMENT_CONVENER",
                    StudentProfile.department_id == department_id,
                ),
            )
            or 0,
        )
        company_count = int(
            self.db.scalar(
                select(func.count(func.distinct(HiringOpportunity.company_id)))
                .select_from(Application)
                .join(
                    HiringOpportunity,
                    HiringOpportunity.id == Application.hiring_opportunity_id,
                )
                .join(
                    StudentProfile,
                    StudentProfile.id == Application.student_profile_id,
                )
                .where(StudentProfile.department_id == department_id),
            )
            or 0,
        )
        return DepartmentCounts(
            student_count=student_count,
            convener_count=convener_count,
            company_count=company_count,
        )

    # ---- Seasons ----

    def list_seasons(
        self,
        *,
        search: str | None,
        status: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[PlacementSeason], int]:
        stmt = select(PlacementSeason)
        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(PlacementSeason.name).like(term),
                    func.lower(PlacementSeason.academic_batch).like(term),
                ),
            )
        if status:
            stmt = stmt.where(PlacementSeason.status == status)

        total = int(
            self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0,
        )
        rows = list(
            self.db.scalars(
                stmt.order_by(
                    PlacementSeason.is_current.desc(),
                    PlacementSeason.start_date.desc(),
                )
                .offset((page - 1) * page_size)
                .limit(page_size),
            ).all(),
        )
        return rows, total

    def get_season(self, season_id: uuid.UUID) -> PlacementSeason | None:
        return self.db.get(PlacementSeason, season_id)

    def add_season(self, season: PlacementSeason) -> PlacementSeason:
        self.db.add(season)
        self.db.flush()
        return season

    def clear_current_active(self) -> None:
        seasons = list(
            self.db.scalars(
                select(PlacementSeason).where(
                    or_(
                        PlacementSeason.is_current.is_(True),
                        PlacementSeason.status == "active",
                    ),
                ),
            ).all(),
        )
        for season in seasons:
            season.is_current = False
            if season.status == "active":
                season.status = "planning"
            season.updated_at = utc_now()

    def season_stats(self, season_id: uuid.UUID) -> dict[str, int]:
        applications = int(
            self.db.scalar(
                select(func.count())
                .select_from(Application)
                .where(Application.season_id == season_id),
            )
            or 0,
        )
        companies = int(
            self.db.scalar(
                select(func.count(func.distinct(HiringOpportunity.company_id)))
                .select_from(HiringOpportunity)
                .where(HiringOpportunity.season_id == season_id),
            )
            or 0,
        )
        students = int(
            self.db.scalar(
                select(func.count(func.distinct(Application.student_profile_id)))
                .select_from(Application)
                .where(Application.season_id == season_id),
            )
            or 0,
        )
        offers = int(
            self.db.scalar(
                select(func.count())
                .select_from(Application)
                .where(
                    Application.season_id == season_id,
                    Application.status.in_(
                        [
                            ApplicationStatus.OFFER_RELEASED,
                            ApplicationStatus.SELECTED,
                            ApplicationStatus.ACCEPTED,
                        ],
                    ),
                ),
            )
            or 0,
        )
        return {
            "applications": applications,
            "companies": companies,
            "students": students,
            "offers": offers,
        }
