from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

from sqlalchemy import String, cast, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.students.models import (
    StudentProfile,
    StudentVerification,
)
from app.modules.users.models import Role, User, UserRole, UserRoleHistory
from app.utils.datetime import utc_now


@dataclass
class UserListRow:
    user: User
    department_name: str | None
    department_code: str | None
    roll_number: str | None
    registration_number: str | None
    graduation_year: int | None
    verification_status: str | None
    profile_status: str | None
    student_profile_id: uuid.UUID | None
    primary_role: str | None


class AdminUserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_users(
        self,
        *,
        search: str | None,
        role: str | None,
        status: str | None,
        department_id: uuid.UUID | None,
        verification: str | None,
        graduation_year: int | None,
        sort_by: str,
        sort_order: str,
        page: int,
        page_size: int,
    ) -> tuple[list[UserListRow], int]:
        from app.modules.students.models import Department

        primary_role_sq = (
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(
                UserRole.user_id == User.id,
                UserRole.is_primary.is_(True),
            )
            .correlate(User)
            .limit(1)
            .scalar_subquery()
        )

        stmt = (
            select(
                User,
                Department.name,
                Department.code,
                StudentProfile.roll_number,
                StudentProfile.registration_number,
                StudentProfile.graduation_year,
                StudentVerification.overall_status,
                StudentProfile.profile_status,
                StudentProfile.id,
                primary_role_sq,
            )
            .options(selectinload(User.roles))
            .outerjoin(StudentProfile, StudentProfile.user_id == User.id)
            .outerjoin(Department, Department.id == StudentProfile.department_id)
            .outerjoin(
                StudentVerification,
                StudentVerification.student_profile_id == StudentProfile.id,
            )
        )

        if search and search.strip():
            term = f"%{search.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(User.first_name).like(term),
                    func.lower(User.last_name).like(term),
                    func.lower(User.display_name).like(term),
                    func.lower(User.college_email).like(term),
                    func.lower(StudentProfile.roll_number).like(term),
                    func.lower(StudentProfile.registration_number).like(term),
                    func.lower(Department.name).like(term),
                    func.lower(Department.code).like(term),
                ),
            )

        if status:
            stmt = stmt.where(User.status == status)

        if department_id:
            stmt = stmt.where(StudentProfile.department_id == department_id)

        if graduation_year:
            stmt = stmt.where(StudentProfile.graduation_year == graduation_year)

        if verification:
            stmt = stmt.where(
                cast(StudentVerification.overall_status, String) == verification,
            )

        if role:
            role_user_ids = (
                select(UserRole.user_id)
                .join(Role, Role.id == UserRole.role_id)
                .where(Role.name == role)
            )
            stmt = stmt.where(User.id.in_(role_user_ids))

        count_stmt = select(func.count()).select_from(stmt.order_by(None).subquery())
        total = int(self.db.scalar(count_stmt) or 0)

        sort_map = {
            "name": User.display_name,
            "email": User.college_email,
            "status": User.status,
            "last_login": User.last_login,
            "created_at": User.created_at,
        }
        sort_col = sort_map.get(sort_by, User.created_at)
        if sort_order == "asc":
            stmt = stmt.order_by(sort_col.asc().nulls_last(), User.id.asc())
        else:
            stmt = stmt.order_by(sort_col.desc().nulls_last(), User.id.desc())

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        rows = self.db.execute(stmt).all()

        items: list[UserListRow] = []
        for row in rows:
            (
                user,
                dept_name,
                dept_code,
                roll,
                reg,
                grad_year,
                ver_status,
                profile_status,
                profile_id,
                primary_role,
            ) = row
            items.append(
                UserListRow(
                    user=user,
                    department_name=dept_name,
                    department_code=dept_code,
                    roll_number=roll,
                    registration_number=reg,
                    graduation_year=grad_year,
                    verification_status=(
                        ver_status.value if hasattr(ver_status, "value") else ver_status
                    ),
                    profile_status=(
                        profile_status.value
                        if hasattr(profile_status, "value")
                        else profile_status
                    ),
                    student_profile_id=profile_id,
                    primary_role=primary_role,
                ),
            )
        return items, total

    def get_user_detail_row(self, user_id: uuid.UUID) -> UserListRow | None:
        user = self.db.scalars(
            select(User).options(selectinload(User.roles)).where(User.id == user_id),
        ).first()
        if user is None:
            return None

        profile = self.db.scalars(
            select(StudentProfile)
            .options(
                selectinload(StudentProfile.department),
                selectinload(StudentProfile.verification),
            )
            .where(StudentProfile.user_id == user_id),
        ).first()

        primary = self.db.scalars(
            select(Role.name)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id, UserRole.is_primary.is_(True)),
        ).first()

        dept = profile.department if profile else None
        verification = profile.verification if profile else None
        return UserListRow(
            user=user,
            department_name=dept.name if dept else None,
            department_code=dept.code if dept else None,
            roll_number=profile.roll_number if profile else None,
            registration_number=profile.registration_number if profile else None,
            graduation_year=profile.graduation_year if profile else None,
            verification_status=(
                verification.overall_status.value
                if verification and hasattr(verification.overall_status, "value")
                else (str(verification.overall_status) if verification else None)
            ),
            profile_status=(
                profile.profile_status.value
                if profile and hasattr(profile.profile_status, "value")
                else (str(profile.profile_status) if profile else None)
            ),
            student_profile_id=profile.id if profile else None,
            primary_role=primary,
        )

    def list_role_assignments(self, user_id: uuid.UUID) -> list[tuple[UserRole, Role]]:
        stmt = (
            select(UserRole, Role)
            .join(Role, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.name)
        )
        return list(self.db.execute(stmt).all())

    def get_user_role(self, user_id: uuid.UUID, role_id: uuid.UUID) -> UserRole | None:
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.role_id == role_id,
        )
        return self.db.scalars(stmt).first()

    def assign_role(
        self,
        user_id: uuid.UUID,
        role: Role,
        *,
        is_primary: bool = False,
        performed_by: uuid.UUID,
    ) -> UserRole:
        existing = self.get_user_role(user_id, role.id)
        if existing is not None:
            if is_primary and not existing.is_primary:
                self.clear_primary(user_id)
                existing.is_primary = True
            return existing

        if is_primary:
            self.clear_primary(user_id)

        link = UserRole(user_id=user_id, role_id=role.id, is_primary=is_primary)
        self.db.add(link)
        self.db.add(
            UserRoleHistory(
                user_id=user_id,
                role_id=role.id,
                role_name=role.name,
                action="ASSIGNED",
                performed_by=performed_by,
                is_primary=is_primary,
            ),
        )
        self.db.flush()
        return link

    def remove_role(
        self,
        user_id: uuid.UUID,
        role: Role,
        *,
        performed_by: uuid.UUID,
    ) -> bool:
        link = self.get_user_role(user_id, role.id)
        if link is None:
            return False
        was_primary = link.is_primary
        self.db.delete(link)
        self.db.add(
            UserRoleHistory(
                user_id=user_id,
                role_id=role.id,
                role_name=role.name,
                action="REMOVED",
                performed_by=performed_by,
                is_primary=was_primary,
            ),
        )
        self.db.flush()
        return True

    def clear_primary(self, user_id: uuid.UUID) -> None:
        stmt = select(UserRole).where(
            UserRole.user_id == user_id,
            UserRole.is_primary.is_(True),
        )
        for link in self.db.scalars(stmt).all():
            link.is_primary = False

    def set_primary_role(self, user_id: uuid.UUID, role: Role) -> None:
        link = self.get_user_role(user_id, role.id)
        if link is None:
            return
        self.clear_primary(user_id)
        link.is_primary = True
        self.db.flush()

    def list_role_history(self, user_id: uuid.UUID, limit: int = 50) -> list[UserRoleHistory]:
        stmt = (
            select(UserRoleHistory)
            .where(UserRoleHistory.user_id == user_id)
            .order_by(UserRoleHistory.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).all())

    def count_applications(self, student_profile_id: uuid.UUID | None) -> int:
        if student_profile_id is None:
            return 0
        from app.modules.applications.models import Application

        return int(
            self.db.scalar(
                select(func.count())
                .select_from(Application)
                .where(Application.student_profile_id == student_profile_id),
            )
            or 0,
        )

    def get_role_by_name(self, name: str) -> Role | None:
        return self.db.scalars(select(Role).where(Role.name == name)).first()

    def touch_user(self, user: User) -> None:
        user.updated_at = utc_now()


def total_pages(total: int, page_size: int) -> int:
    if page_size <= 0:
        return 0
    return max(1, math.ceil(total / page_size)) if total else 0
