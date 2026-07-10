"""Match parsed shortlist rows to opportunity applications."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from app.modules.applications.enums import ApplicationStatus
from app.modules.applications.models import Application
from app.modules.imports.enums import MatchField, RowMatchStatus
from app.modules.imports.parser import ParsedRow
from app.modules.students.models import StudentProfile
from app.modules.users.models import User


@dataclass
class MatchCandidate:
    application_id: UUID
    student_name: str | None
    current_status: ApplicationStatus
    keys: set[str]


@dataclass
class MatchedRowResult:
    row_number: int
    raw_identifier: str
    match_status: RowMatchStatus
    application_id: UUID | None = None
    student_name: str | None = None
    current_status: ApplicationStatus | None = None
    message: str | None = None


def normalize_identifier(value: str, match_field: MatchField) -> str:
    cleaned = value.strip()
    if match_field == MatchField.EMAIL:
        return cleaned.lower()
    return cleaned


def student_display_name(profile: StudentProfile) -> str | None:
    personal = profile.personal_information
    if personal is None:
        return None
    name = f"{personal.first_name} {personal.last_name}".strip()
    return name or None


def build_lookup(
    applications: list[Application],
    profiles: dict[UUID, StudentProfile],
    users: dict[UUID, User],
    match_field: MatchField,
) -> dict[str, list[MatchCandidate]]:
    lookup: dict[str, list[MatchCandidate]] = defaultdict(list)

    for app in applications:
        profile = profiles.get(app.student_profile_id)
        if profile is None:
            continue

        keys: set[str] = set()
        if match_field == MatchField.ROLL_NUMBER and profile.roll_number:
            keys.add(normalize_identifier(profile.roll_number, match_field))
        elif match_field == MatchField.REGISTRATION_NUMBER and profile.registration_number:
            keys.add(normalize_identifier(profile.registration_number, match_field))
        elif match_field == MatchField.EMAIL:
            user = users.get(profile.user_id)
            if user and user.college_email:
                keys.add(normalize_identifier(user.college_email, match_field))
            personal = profile.personal_information
            if personal and personal.personal_email:
                keys.add(normalize_identifier(personal.personal_email, match_field))

        if not keys:
            continue

        candidate = MatchCandidate(
            application_id=app.id,
            student_name=student_display_name(profile),
            current_status=app.status,
            keys=keys,
        )
        for key in keys:
            lookup[key].append(candidate)

    return lookup


def match_rows(
    parsed_rows: list[ParsedRow],
    applications: list[Application],
    profiles: dict[UUID, StudentProfile],
    users: dict[UUID, User],
    match_field: MatchField,
) -> list[MatchedRowResult]:
    lookup = build_lookup(applications, profiles, users, match_field)

    # File-level duplicates by normalized identifier
    counts: dict[str, int] = defaultdict(int)
    normalized_by_row: list[str | None] = []
    for row in parsed_rows:
        if not row.identifier.strip():
            normalized_by_row.append(None)
            continue
        key = normalize_identifier(row.identifier, match_field)
        counts[key] += 1
        normalized_by_row.append(key)

    results: list[MatchedRowResult] = []
    for row, key in zip(parsed_rows, normalized_by_row, strict=True):
        raw = row.identifier.strip()
        if key is None:
            results.append(
                MatchedRowResult(
                    row_number=row.row_number,
                    raw_identifier=raw,
                    match_status=RowMatchStatus.INVALID,
                    message="Missing identifier",
                )
            )
            continue

        if counts[key] > 1:
            results.append(
                MatchedRowResult(
                    row_number=row.row_number,
                    raw_identifier=raw,
                    match_status=RowMatchStatus.DUPLICATE,
                    message="Duplicate identifier in file",
                )
            )
            continue

        candidates = lookup.get(key, [])
        # Deduplicate candidates that matched via multiple email keys
        unique: dict[UUID, MatchCandidate] = {
            c.application_id: c for c in candidates
        }
        unique_list = list(unique.values())

        if len(unique_list) == 0:
            results.append(
                MatchedRowResult(
                    row_number=row.row_number,
                    raw_identifier=raw,
                    match_status=RowMatchStatus.UNMATCHED,
                    message="No application found for this identifier",
                )
            )
        elif len(unique_list) > 1:
            results.append(
                MatchedRowResult(
                    row_number=row.row_number,
                    raw_identifier=raw,
                    match_status=RowMatchStatus.DUPLICATE,
                    message="Multiple applications match this identifier",
                )
            )
        else:
            hit = unique_list[0]
            results.append(
                MatchedRowResult(
                    row_number=row.row_number,
                    raw_identifier=raw,
                    match_status=RowMatchStatus.MATCHED,
                    application_id=hit.application_id,
                    student_name=hit.student_name,
                    current_status=hit.current_status,
                )
            )

    return results
