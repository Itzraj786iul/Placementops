"""Unit tests for shortlist import parser and matcher."""

import io
from types import SimpleNamespace
from uuid import uuid4

from openpyxl import Workbook

from app.modules.applications.enums import ApplicationStatus
from app.modules.imports.enums import MatchField, RowMatchStatus
from app.modules.imports.matcher import match_rows, normalize_identifier
from app.modules.imports.parser import parse_csv, parse_shortlist_file, parse_xlsx


def test_parse_csv_by_roll_number() -> None:
    content = b"Roll Number,Name\n2022CS001,Ada\n2022CS002,Grace\n"
    rows = parse_csv(content, MatchField.ROLL_NUMBER)
    assert len(rows) == 2
    assert rows[0].identifier == "2022CS001"
    assert rows[0].row_number == 2


def test_parse_csv_single_column_fallback() -> None:
    content = b"Identifier\nREG001\n"
    rows = parse_csv(content, MatchField.REGISTRATION_NUMBER)
    assert len(rows) == 1
    assert rows[0].identifier == "REG001"


def test_parse_xlsx_by_email() -> None:
    wb = Workbook()
    ws = wb.active
    assert ws is not None
    ws.append(["Email", "Notes"])
    ws.append(["ada@nitrr.ac.in", "ok"])
    buf = io.BytesIO()
    wb.save(buf)
    rows = parse_xlsx(buf.getvalue(), MatchField.EMAIL)
    assert len(rows) == 1
    assert rows[0].identifier == "ada@nitrr.ac.in"


def test_parse_rejects_unsupported_extension() -> None:
    try:
        parse_shortlist_file("list.pdf", b"x", MatchField.ROLL_NUMBER)
        assert False, "expected validation error"
    except Exception as exc:
        assert "Unsupported" in str(exc)


def test_normalize_email_case() -> None:
    assert normalize_identifier("Ada@NITRR.ac.in", MatchField.EMAIL) == "ada@nitrr.ac.in"


def _profile(
    *,
    roll: str,
    reg: str,
    personal_email: str | None = None,
    first: str = "Ada",
    last: str = "Lovelace",
) -> SimpleNamespace:
    user_id = uuid4()
    personal = None
    if personal_email is not None or first:
        personal = SimpleNamespace(
            first_name=first,
            last_name=last,
            personal_email=personal_email,
        )
    return SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        roll_number=roll,
        registration_number=reg,
        personal_information=personal,
    )


def test_match_rows_matched_unmatched_duplicate_invalid() -> None:
    profile = _profile(roll="2022CS001", reg="REG001", personal_email="ada@ex.com")
    app = SimpleNamespace(
        id=uuid4(),
        student_profile_id=profile.id,
        status=ApplicationStatus.APPLIED,
    )
    user = SimpleNamespace(id=profile.user_id, college_email="ada@nitrr.ac.in")

    from app.modules.imports.parser import ParsedRow

    parsed = [
        ParsedRow(2, "2022CS001"),
        ParsedRow(3, "UNKNOWN"),
        ParsedRow(4, "DUP"),
        ParsedRow(5, "DUP"),
        ParsedRow(6, "   "),
    ]
    results = match_rows(
        parsed,
        [app],  # type: ignore[arg-type]
        {profile.id: profile},  # type: ignore[arg-type]
        {user.id: user},  # type: ignore[arg-type]
        MatchField.ROLL_NUMBER,
    )
    statuses = [r.match_status for r in results]
    assert statuses == [
        RowMatchStatus.MATCHED,
        RowMatchStatus.UNMATCHED,
        RowMatchStatus.DUPLICATE,
        RowMatchStatus.DUPLICATE,
        RowMatchStatus.INVALID,
    ]
    assert results[0].application_id == app.id
    assert results[0].student_name == "Ada Lovelace"


def test_match_by_college_or_personal_email() -> None:
    profile = _profile(roll="R1", reg="G1", personal_email="personal@ex.com")
    app = SimpleNamespace(
        id=uuid4(),
        student_profile_id=profile.id,
        status=ApplicationStatus.SHORTLISTED,
    )
    user = SimpleNamespace(id=profile.user_id, college_email="college@nitrr.ac.in")

    from app.modules.imports.parser import ParsedRow

    for email in ("college@nitrr.ac.in", "PERSONAL@EX.COM"):
        results = match_rows(
            [ParsedRow(2, email)],
            [app],  # type: ignore[arg-type]
            {profile.id: profile},  # type: ignore[arg-type]
            {user.id: user},  # type: ignore[arg-type]
            MatchField.EMAIL,
        )
        assert results[0].match_status == RowMatchStatus.MATCHED


def test_importable_statuses_cover_required() -> None:
    from app.modules.imports.enums import IMPORTABLE_STATUSES

    required = {
        ApplicationStatus.SHORTLISTED,
        ApplicationStatus.ASSESSMENT,
        ApplicationStatus.INTERVIEW,
        ApplicationStatus.SELECTED,
        ApplicationStatus.OFFER_RELEASED,
        ApplicationStatus.REJECTED,
    }
    assert required == IMPORTABLE_STATUSES
