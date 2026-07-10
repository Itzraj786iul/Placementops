import uuid
from datetime import datetime, timezone
from types import SimpleNamespace

from app.modules.applications.enums import ApplicationStatus
from app.modules.exports.enums import DEFAULT_COLUMNS, ExportColumn, ExportFormat, ExportScope
from app.modules.exports.generators import build_csv, build_xlsx
from app.modules.exports.projector import project_row
from app.modules.exports.schemas import ExportFilters, ExportRequest


def _application_with_snapshot() -> SimpleNamespace:
    app_id = uuid.uuid4()
    snapshot = SimpleNamespace(
        application_id=app_id,
        student_profile_snapshot={
            "roll_number": "2022CS001",
            "registration_number": "REG001",
            "department_name": "Computer Science",
            "department_code": "CSE",
            "graduation_year": 2026,
            "personal_information": {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "gender": "FEMALE",
                "personal_email": "ada@example.com",
                "phone_number": "9999999999",
            },
            "academic_information": {
                "current_cgpa": "8.50",
                "active_backlogs": 0,
                "total_history_backlogs": 1,
            },
        },
        resume_snapshot={"name": "Primary Resume", "version": 1},
        eligibility_snapshot={},
    )
    return SimpleNamespace(
        id=app_id,
        student_profile_id=uuid.uuid4(),
        hiring_opportunity_id=uuid.uuid4(),
        selected_resume_id=uuid.uuid4(),
        status=ApplicationStatus.APPLIED,
        applied_at=datetime(2026, 7, 1, 10, 0, tzinfo=timezone.utc),
        snapshot=snapshot,
    )


def test_project_default_columns() -> None:
    application = _application_with_snapshot()
    row = project_row(
        application,  # type: ignore[arg-type]
        columns=DEFAULT_COLUMNS,
        company_name="Acme Corp",
        eligible=True,
    )
    assert row["roll_number"] == "2022CS001"
    assert row["student_name"] == "Ada Lovelace"
    assert row["department"] == "Computer Science"
    assert row["cgpa"] == "8.50"
    assert row["active_backlogs"] == "0"
    assert row["history_backlogs"] == "1"
    assert row["resume_used"] == "Primary Resume"
    assert row["application_status"] == "APPLIED"


def test_build_csv_contains_headers_and_row() -> None:
    application = _application_with_snapshot()
    columns = [ExportColumn.ROLL_NUMBER, ExportColumn.STUDENT_NAME]
    rows = [
        project_row(
            application,  # type: ignore[arg-type]
            columns=columns,
            company_name=None,
            eligible=None,
        ),
    ]
    content = build_csv(columns, rows).decode("utf-8-sig")
    assert "Roll Number" in content
    assert "Student Name" in content
    assert "2022CS001" in content
    assert "Ada Lovelace" in content


def test_build_xlsx_produces_bytes() -> None:
    application = _application_with_snapshot()
    columns = [ExportColumn.ROLL_NUMBER, ExportColumn.CGPA]
    rows = [
        project_row(
            application,  # type: ignore[arg-type]
            columns=columns,
            company_name=None,
            eligible=False,
        ),
    ]
    content = build_xlsx(columns, rows)
    assert isinstance(content, bytes)
    assert len(content) > 0
    assert content[:2] == b"PK"


def test_export_request_rejects_empty_columns() -> None:
    try:
        ExportRequest(columns=[])
        assert False, "Expected validation error"
    except Exception:
        pass


def test_export_request_defaults() -> None:
    payload = ExportRequest()
    assert payload.format == ExportFormat.XLSX
    assert payload.scope == ExportScope.ALL
    assert payload.columns == DEFAULT_COLUMNS
    assert isinstance(payload.filters, ExportFilters)


def test_eligibility_column_projection() -> None:
    application = _application_with_snapshot()
    row = project_row(
        application,  # type: ignore[arg-type]
        columns=[ExportColumn.ELIGIBILITY, ExportColumn.COMPANY],
        company_name="NITRR Partner",
        eligible=False,
    )
    assert row["eligibility"] == "Ineligible"
    assert row["company"] == "NITRR Partner"
