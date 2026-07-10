from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.applications.enums import ApplicationStatus
from app.modules.applications.transitions import validate_staff_status_update
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.imports.access import ensure_staff_access
from app.modules.imports.enums import IMPORTABLE_STATUSES, ImportStatus, MatchField, RowMatchStatus
from app.modules.imports.exceptions import (
    ImportNotFoundError,
    ImportValidationError,
)
from app.modules.imports.matcher import match_rows
from app.modules.imports.models import ShortlistImport, ShortlistImportRow
from app.modules.imports.parser import parse_shortlist_file
from app.modules.imports.repository import ImportRepository
from app.modules.imports.schemas import ImportConfirmResponse, ImportPreviewResponse
from app.modules.users.models import User
from app.utils.datetime import utc_now


class ImportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = ImportRepository(db)

    def preview(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        *,
        filename: str,
        content: bytes,
        match_field: MatchField,
        target_status: ApplicationStatus,
    ) -> ImportPreviewResponse:
        ensure_staff_access(user)

        if target_status not in IMPORTABLE_STATUSES:
            raise ImportValidationError(
                f"Status {target_status.value} is not supported for shortlist import",
            )

        opportunity = self.repository.get_opportunity(opportunity_id)
        if opportunity is None:
            raise ImportNotFoundError("Hiring opportunity not found")

        parsed = parse_shortlist_file(filename, content, match_field)
        applications = self.repository.list_applications(opportunity_id)
        profile_ids = [app.student_profile_id for app in applications]
        profiles_list = self.repository.get_profiles_by_ids(profile_ids)
        profiles = {p.id: p for p in profiles_list}
        user_ids = [p.user_id for p in profiles_list]
        users_list = self.repository.get_users_by_ids(user_ids)
        users = {u.id: u for u in users_list}

        matched = match_rows(parsed, applications, profiles, users, match_field)

        import_record = ShortlistImport(
            hiring_opportunity_id=opportunity_id,
            imported_by=user.id,
            filename=filename[:255],
            match_field=match_field,
            target_status=target_status,
            status=ImportStatus.PREVIEW,
            total_rows=len(matched),
            matched_rows=sum(1 for r in matched if r.match_status == RowMatchStatus.MATCHED),
            unmatched_rows=sum(
                1 for r in matched if r.match_status == RowMatchStatus.UNMATCHED
            ),
            duplicate_rows=sum(
                1 for r in matched if r.match_status == RowMatchStatus.DUPLICATE
            ),
            invalid_rows=sum(1 for r in matched if r.match_status == RowMatchStatus.INVALID),
        )
        self.repository.add(import_record)
        self.repository.flush()

        for result in matched:
            self.repository.add(
                ShortlistImportRow(
                    import_id=import_record.id,
                    row_number=result.row_number,
                    raw_identifier=result.raw_identifier[:255],
                    match_status=result.match_status,
                    application_id=result.application_id,
                    student_name=result.student_name,
                    current_status=result.current_status,
                    message=(result.message[:500] if result.message else None),
                )
            )

        self.repository.commit()
        saved = self.repository.get_import(import_record.id, opportunity_id)
        assert saved is not None
        return ImportPreviewResponse.model_validate(saved)

    def confirm(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        import_id: uuid.UUID,
    ) -> ImportConfirmResponse:
        ensure_staff_access(user)

        import_record = self.repository.get_import(import_id, opportunity_id)
        if import_record is None:
            raise ImportNotFoundError()

        if import_record.status != ImportStatus.PREVIEW:
            raise ImportValidationError("Import has already been confirmed")

        updated = 0
        skipped = 0
        status_updates: list[tuple[uuid.UUID, ApplicationStatus, ApplicationStatus]] = []

        for row in import_record.rows:
            if row.match_status != RowMatchStatus.MATCHED or row.application_id is None:
                skipped += 1
                continue

            application = self.repository.get_application(row.application_id)
            if application is None:
                skipped += 1
                row.message = "Application no longer exists"
                continue

            try:
                validate_staff_status_update(
                    application.status,
                    import_record.target_status,
                )
            except ValueError as exc:
                skipped += 1
                row.message = str(exc)
                continue

            old_status = application.status
            application.status = import_record.target_status
            row.current_status = import_record.target_status
            updated += 1
            status_updates.append(
                (application.id, old_status, import_record.target_status),
            )

        import_record.status = ImportStatus.CONFIRMED
        import_record.rows_updated = updated
        import_record.rows_skipped = skipped
        import_record.confirmed_at = utc_now()

        record_audit(
            self.db,
            entity_type=AuditEntityType.SHORTLIST_IMPORT,
            entity_id=import_record.id,
            action=AuditAction.SHORTLIST_IMPORTED,
            performed_by=user.id,
            new_values={
                "target_status": import_record.target_status.value,
                "match_field": import_record.match_field.value,
                "rows_updated": updated,
                "rows_skipped": skipped,
                "filename": import_record.filename,
            },
            metadata={
                "hiring_opportunity_id": str(opportunity_id),
                "matched_rows": import_record.matched_rows,
                "unmatched_rows": import_record.unmatched_rows,
                "duplicate_rows": import_record.duplicate_rows,
                "invalid_rows": import_record.invalid_rows,
            },
        )
        from app.platform.notifications.triggers import notify_shortlist_import_affected

        opportunity = self.repository.get_opportunity(opportunity_id)
        notify_shortlist_import_affected(
            self.db,
            updates=status_updates,
            opportunity=opportunity,
        )
        self.repository.commit()

        refreshed = self.repository.get_import(import_id, opportunity_id)
        assert refreshed is not None
        return ImportConfirmResponse(
            id=refreshed.id,
            status=refreshed.status,
            target_status=refreshed.target_status,
            imported_by=refreshed.imported_by,
            imported_at=refreshed.imported_at,
            confirmed_at=refreshed.confirmed_at,
            rows_updated=refreshed.rows_updated or 0,
            rows_skipped=refreshed.rows_skipped or 0,
            matched_rows=refreshed.matched_rows,
            unmatched_rows=refreshed.unmatched_rows,
            duplicate_rows=refreshed.duplicate_rows,
            invalid_rows=refreshed.invalid_rows,
        )
