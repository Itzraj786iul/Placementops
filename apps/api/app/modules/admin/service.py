from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.admin.access import (
    ensure_admin_access,
    is_super_admin,
    target_has_role,
)
from app.modules.admin.exceptions import (
    AdminForbiddenError,
    AdminNotFoundError,
    AdminValidationError,
)
from app.modules.admin.repository import AdminUserRepository, total_pages
from app.modules.admin.schemas import (
    AdminAuditItem,
    AdminAuditListResponse,
    AdminBulkResult,
    AdminBulkUpdate,
    AdminRolesUpdate,
    AdminUserDetail,
    AdminUserListItem,
    AdminUserListResponse,
    AdminUserUpdate,
    RoleAssignmentResponse,
    RoleHistoryItem,
    user_is_active,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.audit.repository import AuditRepository
from app.modules.users.models import (
    USER_STATUS_ACTIVE,
    USER_STATUS_ARCHIVED,
    USER_STATUS_INACTIVE,
    USER_STATUS_SUSPENDED,
    USER_STATUSES,
    User,
)
from app.modules.users.schemas import RoleResponse


class AdminUserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = AdminUserRepository(db)
        self.audit_repository = AuditRepository(db)

    def list_users(
        self,
        actor: User,
        *,
        search: str | None = None,
        role: str | None = None,
        status: str | None = None,
        department_id: uuid.UUID | None = None,
        verification: str | None = None,
        graduation_year: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        page_size: int = 20,
    ) -> AdminUserListResponse:
        ensure_admin_access(actor)
        rows, total = self.repository.list_users(
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
        return AdminUserListResponse(
            items=[self._to_list_item(row) for row in rows],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages(total, page_size),
        )

    def get_user(self, actor: User, user_id: uuid.UUID) -> AdminUserDetail:
        ensure_admin_access(actor)
        row = self.repository.get_user_detail_row(user_id)
        if row is None:
            raise AdminNotFoundError()

        assignments = self.repository.list_role_assignments(user_id)
        history = self.repository.list_role_history(user_id)
        app_count = self.repository.count_applications(row.student_profile_id)

        return AdminUserDetail(
            id=row.user.id,
            college_email=row.user.college_email,
            personal_email=row.user.personal_email,
            first_name=row.user.first_name,
            last_name=row.user.last_name,
            display_name=row.user.display_name,
            profile_picture=row.user.avatar_url,
            status=row.user.status,
            is_active=user_is_active(row.user),
            email_verified=row.user.email_verified,
            roles=[RoleResponse.model_validate(r) for r in row.user.roles],
            role_assignments=[
                RoleAssignmentResponse(
                    role_id=role.id,
                    role_name=role.name,
                    is_primary=link.is_primary,
                )
                for link, role in assignments
            ],
            primary_role=row.primary_role,
            department_name=row.department_name,
            department_code=row.department_code,
            roll_number=row.roll_number,
            registration_number=row.registration_number,
            graduation_year=row.graduation_year,
            profile_status=row.profile_status,
            verification_status=row.verification_status,
            student_profile_id=row.student_profile_id,
            last_login=row.user.last_login,
            created_at=row.user.created_at,
            updated_at=row.user.updated_at,
            role_history=[
                RoleHistoryItem(
                    id=h.id,
                    role_name=h.role_name,
                    action=h.action,
                    performed_by=h.performed_by,
                    is_primary=h.is_primary,
                    created_at=h.created_at,
                )
                for h in history
            ],
            statistics={
                "applications": app_count,
                "roles": len(row.user.roles),
                "verification": row.verification_status,
            },
            current_sessions=[],
        )

    def update_user(
        self,
        actor: User,
        user_id: uuid.UUID,
        payload: AdminUserUpdate,
    ) -> AdminUserDetail:
        ensure_admin_access(actor)
        row = self.repository.get_user_detail_row(user_id)
        if row is None:
            raise AdminNotFoundError()
        target = row.user
        self._assert_can_modify(actor, target)

        old_values: dict = {}
        new_values: dict = {}

        if payload.status is not None:
            if payload.status not in USER_STATUSES:
                raise AdminValidationError("Invalid status")
            if payload.status == USER_STATUS_ARCHIVED and not is_super_admin(actor):
                raise AdminForbiddenError("Only SUPER_ADMIN can archive users")
            if (
                target_has_role(target, "PLACEMENT_CELL")
                and payload.status in {USER_STATUS_INACTIVE, USER_STATUS_SUSPENDED, USER_STATUS_ARCHIVED}
                and not is_super_admin(actor)
            ):
                raise AdminForbiddenError(
                    "Only SUPER_ADMIN can deactivate Placement Cell accounts",
                )
            old_values["status"] = target.status
            new_values["status"] = payload.status
            target.status = payload.status

        if payload.first_name is not None:
            old_values["first_name"] = target.first_name
            new_values["first_name"] = payload.first_name
            target.first_name = payload.first_name
        if payload.last_name is not None:
            old_values["last_name"] = target.last_name
            new_values["last_name"] = payload.last_name
            target.last_name = payload.last_name
        if payload.display_name is not None:
            old_values["display_name"] = target.display_name
            new_values["display_name"] = payload.display_name
            target.display_name = payload.display_name

        if new_values:
            self.repository.touch_user(target)
            record_audit(
                self.db,
                entity_type=AuditEntityType.USER,
                entity_id=target.id,
                action=AuditAction.UPDATE,
                performed_by=actor.id,
                old_values=old_values or None,
                new_values=new_values,
            )
            self.db.commit()

        return self.get_user(actor, user_id)

    def update_roles(
        self,
        actor: User,
        user_id: uuid.UUID,
        payload: AdminRolesUpdate,
    ) -> AdminUserDetail:
        ensure_admin_access(actor)
        row = self.repository.get_user_detail_row(user_id)
        if row is None:
            raise AdminNotFoundError()
        target = row.user
        self._assert_can_modify(actor, target)

        for role_name in payload.assign:
            self._assert_can_assign_role(actor, role_name)
            role = self.repository.get_role_by_name(role_name)
            if role is None:
                raise AdminValidationError(f"Unknown role: {role_name}")
            self.repository.assign_role(
                user_id,
                role,
                is_primary=payload.primary_role == role_name,
                performed_by=actor.id,
            )
            record_audit(
                self.db,
                entity_type=AuditEntityType.USER,
                entity_id=user_id,
                action=AuditAction.ROLE_ASSIGNED,
                performed_by=actor.id,
                new_values={"role": role_name},
            )

        for role_name in payload.remove:
            self._assert_can_assign_role(actor, role_name)
            role = self.repository.get_role_by_name(role_name)
            if role is None:
                raise AdminValidationError(f"Unknown role: {role_name}")
            removed = self.repository.remove_role(
                user_id,
                role,
                performed_by=actor.id,
            )
            if removed:
                record_audit(
                    self.db,
                    entity_type=AuditEntityType.USER,
                    entity_id=user_id,
                    action=AuditAction.ROLE_REMOVED,
                    performed_by=actor.id,
                    old_values={"role": role_name},
                )

        if payload.primary_role:
            self._assert_can_assign_role(actor, payload.primary_role)
            role = self.repository.get_role_by_name(payload.primary_role)
            if role is None:
                raise AdminValidationError(f"Unknown role: {payload.primary_role}")
            if self.repository.get_user_role(user_id, role.id) is None:
                raise AdminValidationError("Primary role must already be assigned")
            self.repository.set_primary_role(user_id, role)
            record_audit(
                self.db,
                entity_type=AuditEntityType.USER,
                entity_id=user_id,
                action=AuditAction.UPDATE,
                performed_by=actor.id,
                new_values={"primary_role": payload.primary_role},
            )

        self.repository.touch_user(target)
        self.db.commit()
        return self.get_user(actor, user_id)

    def bulk_update(self, actor: User, payload: AdminBulkUpdate) -> AdminBulkResult:
        ensure_admin_access(actor)
        if not payload.confirm:
            raise AdminValidationError("Bulk actions require confirm=true")

        updated = 0
        skipped = 0
        export_rows: list[AdminUserListItem] | None = None

        if payload.action == "export":
            items: list[AdminUserListItem] = []
            for uid in payload.user_ids:
                row = self.repository.get_user_detail_row(uid)
                if row is None:
                    skipped += 1
                    continue
                items.append(self._to_list_item(row))
                updated += 1
            export_rows = items
            self.db.commit()
            return AdminBulkResult(updated=updated, skipped=skipped, export_rows=export_rows)

        for uid in payload.user_ids:
            row = self.repository.get_user_detail_row(uid)
            if row is None:
                skipped += 1
                continue
            target = row.user
            try:
                self._assert_can_modify(actor, target)
            except AdminForbiddenError:
                skipped += 1
                continue

            if payload.action == "activate":
                target.status = USER_STATUS_ACTIVE
                record_audit(
                    self.db,
                    entity_type=AuditEntityType.USER,
                    entity_id=target.id,
                    action=AuditAction.STATUS_CHANGED,
                    performed_by=actor.id,
                    new_values={"status": USER_STATUS_ACTIVE},
                )
                updated += 1
            elif payload.action == "deactivate":
                if target_has_role(target, "PLACEMENT_CELL") and not is_super_admin(actor):
                    skipped += 1
                    continue
                if target_has_role(target, "SUPER_ADMIN") and not is_super_admin(actor):
                    skipped += 1
                    continue
                target.status = USER_STATUS_INACTIVE
                record_audit(
                    self.db,
                    entity_type=AuditEntityType.USER,
                    entity_id=target.id,
                    action=AuditAction.STATUS_CHANGED,
                    performed_by=actor.id,
                    new_values={"status": USER_STATUS_INACTIVE},
                )
                updated += 1
            elif payload.action == "assign_role":
                if not payload.role_name:
                    raise AdminValidationError("role_name is required for assign_role")
                try:
                    self._assert_can_assign_role(actor, payload.role_name)
                except AdminForbiddenError:
                    skipped += 1
                    continue
                role = self.repository.get_role_by_name(payload.role_name)
                if role is None:
                    skipped += 1
                    continue
                self.repository.assign_role(
                    target.id,
                    role,
                    performed_by=actor.id,
                )
                record_audit(
                    self.db,
                    entity_type=AuditEntityType.USER,
                    entity_id=target.id,
                    action=AuditAction.ROLE_ASSIGNED,
                    performed_by=actor.id,
                    new_values={"role": payload.role_name},
                )
                updated += 1

        self.db.commit()
        return AdminBulkResult(updated=updated, skipped=skipped, export_rows=export_rows)

    def get_user_audit(
        self,
        actor: User,
        user_id: uuid.UUID,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> AdminAuditListResponse:
        ensure_admin_access(actor)
        if self.repository.get_user_detail_row(user_id) is None:
            raise AdminNotFoundError()

        offset = (page - 1) * page_size
        entity_rows, entity_total = self.audit_repository.list_logs(
            entity_type=AuditEntityType.USER,
            entity_id=user_id,
            offset=offset,
            limit=page_size,
        )
        actor_rows, actor_total = self.audit_repository.list_logs(
            performed_by=user_id,
            offset=offset,
            limit=page_size,
        )

        merged = {str(item.id): item for item in entity_rows}
        for item in actor_rows:
            merged[str(item.id)] = item
        items = sorted(merged.values(), key=lambda x: x.performed_at, reverse=True)[
            :page_size
        ]

        return AdminAuditListResponse(
            items=[
                AdminAuditItem(
                    id=i.id,
                    entity_type=i.entity_type.value
                    if hasattr(i.entity_type, "value")
                    else str(i.entity_type),
                    entity_id=i.entity_id,
                    action=i.action.value if hasattr(i.action, "value") else str(i.action),
                    performed_by=i.performed_by,
                    performed_at=i.performed_at,
                    old_values=i.old_values,
                    new_values=i.new_values,
                    metadata=i.metadata_,
                )
                for i in items
            ],
            total=entity_total + actor_total,
        )

    def _assert_can_modify(self, actor: User, target: User) -> None:
        if target_has_role(target, "SUPER_ADMIN") and not is_super_admin(actor):
            raise AdminForbiddenError("Placement Cell cannot modify SUPER_ADMIN users")
        if actor.id == target.id and target_has_role(target, "SUPER_ADMIN"):
            # Allow self profile edits but block self-archive via status checks elsewhere
            pass

    def _assert_can_assign_role(self, actor: User, role_name: str) -> None:
        if role_name == "SUPER_ADMIN" and not is_super_admin(actor):
            raise AdminForbiddenError("Only SUPER_ADMIN can assign SUPER_ADMIN")

    def _to_list_item(self, row) -> AdminUserListItem:
        return AdminUserListItem(
            id=row.user.id,
            college_email=row.user.college_email,
            first_name=row.user.first_name,
            last_name=row.user.last_name,
            display_name=row.user.display_name,
            profile_picture=row.user.avatar_url,
            status=row.user.status,
            is_active=user_is_active(row.user),
            roles=[RoleResponse.model_validate(r) for r in row.user.roles],
            primary_role=row.primary_role,
            department_name=row.department_name,
            department_code=row.department_code,
            roll_number=row.roll_number,
            registration_number=row.registration_number,
            verification_status=row.verification_status,
            graduation_year=row.graduation_year,
            last_login=row.user.last_login,
            created_at=row.user.created_at,
        )
