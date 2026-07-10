from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.eligibility.evaluator import evaluate_student, is_eligible
from app.modules.exports.access import ensure_staff_access
from app.modules.exports.enums import ExportColumn, ExportFormat, ExportScope
from app.modules.exports.exceptions import ExportNotFoundError, ExportValidationError
from app.modules.exports.generators import build_csv, build_xlsx
from app.modules.exports.projector import project_row
from app.modules.exports.repository import ExportRepository
from app.modules.exports.schemas import ExportRequest
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.users.models import User


class ExportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ExportRepository(db)

    def export_applications(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        payload: ExportRequest,
    ) -> tuple[bytes, str, str]:
        ensure_staff_access(user)

        opportunity = self.repository.get_opportunity(opportunity_id)
        if opportunity is None:
            raise ExportNotFoundError()

        if (
            payload.filters.company_id is not None
            and payload.filters.company_id != opportunity.company_id
        ):
            raise ExportValidationError(
                "Company filter does not match this opportunity's company",
            )

        company_name = self.repository.get_company_name(opportunity.company_id)
        applications = self.repository.list_applications_with_snapshots(opportunity_id)

        # Status filter
        if payload.filters.status:
            allowed = set(payload.filters.status)
            applications = [app for app in applications if app.status in allowed]

        # Department filter (name or code match against snapshot)
        if payload.filters.department:
            dept_filter = payload.filters.department.strip().lower()
            filtered = []
            for app in applications:
                profile = (
                    app.snapshot.student_profile_snapshot if app.snapshot else {}
                ) or {}
                name = str(profile.get("department_name") or "").lower()
                code = str(profile.get("department_code") or "").lower()
                if dept_filter in (name, code) or dept_filter == name or dept_filter == code:
                    filtered.append(app)
                elif dept_filter in name or dept_filter in code:
                    filtered.append(app)
            applications = filtered

        needs_eligibility = (
            payload.scope != ExportScope.ALL
            or ExportColumn.ELIGIBILITY in payload.columns
        )

        eligibility_map: dict[uuid.UUID, bool] = {}
        if needs_eligibility:
            profile_ids = [app.student_profile_id for app in applications]
            profiles = self.repository.get_profiles_by_ids(profile_ids)
            profile_map = {profile.id: profile for profile in profiles}
            rule = opportunity.eligibility_rule
            for app in applications:
                reasons = evaluate_student(rule, profile_map.get(app.student_profile_id))
                eligibility_map[app.id] = is_eligible(reasons)

        if payload.scope == ExportScope.ELIGIBLE:
            applications = [
                app for app in applications if eligibility_map.get(app.id) is True
            ]
        elif payload.scope == ExportScope.INELIGIBLE:
            applications = [
                app for app in applications if eligibility_map.get(app.id) is False
            ]

        rows = [
            project_row(
                app,
                columns=payload.columns,
                company_name=company_name,
                eligible=eligibility_map.get(app.id) if needs_eligibility else None,
            )
            for app in applications
        ]

        if payload.format == ExportFormat.CSV:
            content = build_csv(payload.columns, rows)
            media_type = "text/csv; charset=utf-8"
            filename = f"opportunity-{opportunity_id}-applications.csv"
        else:
            content = build_xlsx(payload.columns, rows)
            media_type = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            filename = f"opportunity-{opportunity_id}-applications.xlsx"

        record_audit(
            self.db,
            entity_type=AuditEntityType.EXPORT,
            entity_id=opportunity_id,
            action=AuditAction.EXPORT_GENERATED,
            performed_by=user.id,
            new_values={
                "format": payload.format.value,
                "scope": payload.scope.value,
                "columns": [column.value for column in payload.columns],
                "row_count": len(rows),
                "filename": filename,
            },
            metadata={
                "filters": {
                    "status": (
                        [status.value for status in payload.filters.status]
                        if payload.filters.status
                        else None
                    ),
                    "department": payload.filters.department,
                    "company_id": (
                        str(payload.filters.company_id)
                        if payload.filters.company_id
                        else None
                    ),
                },
            },
        )
        self.db.commit()

        return content, media_type, filename
