from __future__ import annotations

from typing import Any, Protocol

from app.modules.exports.enums import ExportColumn


class _ExportableApplication(Protocol):
    status: Any
    applied_at: Any
    snapshot: Any


def _nested(data: dict[str, Any] | None, *keys: str) -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def project_row(
    application: _ExportableApplication,
    *,
    columns: list[ExportColumn],
    company_name: str | None,
    eligible: bool | None,
) -> dict[str, str]:
    snapshot = application.snapshot
    profile = snapshot.student_profile_snapshot if snapshot else {}
    resume = snapshot.resume_snapshot if snapshot else {}
    personal = _nested(profile, "personal_information") or {}
    academic = _nested(profile, "academic_information") or {}

    first = personal.get("first_name") or ""
    last = personal.get("last_name") or ""
    student_name = f"{first} {last}".strip() or ""

    status_value = (
        application.status.value
        if hasattr(application.status, "value")
        else str(application.status)
    )

    values: dict[ExportColumn, str] = {
        ExportColumn.ROLL_NUMBER: str(profile.get("roll_number") or ""),
        ExportColumn.REGISTRATION_NUMBER: str(profile.get("registration_number") or ""),
        ExportColumn.STUDENT_NAME: student_name,
        ExportColumn.DEPARTMENT: str(profile.get("department_name") or ""),
        ExportColumn.DEPARTMENT_CODE: str(profile.get("department_code") or ""),
        ExportColumn.CGPA: str(academic.get("current_cgpa") or ""),
        ExportColumn.ACTIVE_BACKLOGS: (
            "" if academic.get("active_backlogs") is None else str(academic.get("active_backlogs"))
        ),
        ExportColumn.HISTORY_BACKLOGS: (
            ""
            if academic.get("total_history_backlogs") is None
            else str(academic.get("total_history_backlogs"))
        ),
        ExportColumn.GRADUATION_YEAR: (
            "" if profile.get("graduation_year") is None else str(profile.get("graduation_year"))
        ),
        ExportColumn.GENDER: str(personal.get("gender") or ""),
        ExportColumn.PERSONAL_EMAIL: str(personal.get("personal_email") or ""),
        ExportColumn.PHONE_NUMBER: str(personal.get("phone_number") or ""),
        ExportColumn.RESUME_USED: str(resume.get("name") or ""),
        ExportColumn.APPLICATION_STATUS: status_value,
        ExportColumn.APPLIED_AT: (
            application.applied_at.isoformat() if application.applied_at else ""
        ),
        ExportColumn.ELIGIBILITY: (
            "" if eligible is None else ("Eligible" if eligible else "Ineligible")
        ),
        ExportColumn.COMPANY: company_name or "",
    }

    return {column.value: values[column] for column in columns}
