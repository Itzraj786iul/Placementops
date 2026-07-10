from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from app.modules.eligibility.enums import (
    EDUCATION_MIN_SCORE_KEYS,
    REASON_TITLES,
    EligibilityReasonCode,
)
from app.modules.eligibility.schemas import EligibilityReason
from app.modules.hiring_opportunities.models import EligibilityRule
from app.modules.students.models import (
    StudentAcademicInformation,
    StudentEducationHistory,
    StudentPersonalInformation,
    StudentProfile,
)


def _reason(
    code: EligibilityReasonCode,
    expected: str,
    actual: str,
) -> EligibilityReason:
    return EligibilityReason(
        code=code,
        title=REASON_TITLES[code],
        expected=expected,
        actual=actual,
    )


def _parse_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return None


def _format_decimal(value: Decimal | None) -> str:
    if value is None:
        return "—"
    return format(value, "f")


def evaluate_student(
    rule: EligibilityRule | None,
    profile: StudentProfile | None,
) -> list[EligibilityReason]:
    """
    Deterministically evaluate a student against eligibility rules.

    Returns ALL failed checks — never short-circuits on first failure.
    An empty list means eligible.
    """
    reasons: list[EligibilityReason] = []

    if profile is None:
        reasons.append(
            _reason(
                EligibilityReasonCode.PROFILE_MISSING,
                expected="Complete student profile",
                actual="Missing",
            ),
        )
        return reasons

    # No rule configured → everyone is eligible (nothing to fail).
    if rule is None:
        return reasons

    academic: StudentAcademicInformation | None = profile.academic_information
    personal: StudentPersonalInformation | None = profile.personal_information
    education_history: list[StudentEducationHistory] = list(
        profile.education_history or [],
    )

    reasons.extend(_check_cgpa(rule, academic))
    reasons.extend(_check_department(rule, profile))
    reasons.extend(_check_graduation_year(rule, profile))
    reasons.extend(_check_active_backlogs(rule, academic))
    reasons.extend(_check_backlog_history(rule, academic))
    reasons.extend(_check_gender(rule, personal))
    reasons.extend(_check_education_requirements(rule, education_history))

    return reasons


def _check_cgpa(
    rule: EligibilityRule,
    academic: StudentAcademicInformation | None,
) -> list[EligibilityReason]:
    if rule.minimum_cgpa is None:
        return []

    expected = _format_decimal(rule.minimum_cgpa)

    if academic is None:
        return [
            _reason(
                EligibilityReasonCode.ACADEMIC_INFO_MISSING,
                expected=f"CGPA >= {expected}",
                actual="Academic information not provided",
            ),
        ]

    actual_cgpa = academic.current_cgpa
    if actual_cgpa is None or actual_cgpa < rule.minimum_cgpa:
        return [
            _reason(
                EligibilityReasonCode.CGPA_BELOW_MINIMUM,
                expected=f">= {expected}",
                actual=_format_decimal(actual_cgpa),
            ),
        ]
    return []


def _check_department(
    rule: EligibilityRule,
    profile: StudentProfile,
) -> list[EligibilityReason]:
    allowed = rule.allowed_departments
    if not allowed:
        return []

    allowed_ids = {str(item) for item in allowed}
    actual_id = str(profile.department_id)
    if actual_id in allowed_ids:
        return []

    dept_name = profile.department.name if profile.department else actual_id
    return [
        _reason(
            EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED,
            expected="One of allowed departments",
            actual=dept_name,
        ),
    ]


def _check_graduation_year(
    rule: EligibilityRule,
    profile: StudentProfile,
) -> list[EligibilityReason]:
    allowed = rule.allowed_graduation_years
    if not allowed:
        return []

    allowed_years = [int(year) for year in allowed]
    if profile.graduation_year in allowed_years:
        return []

    return [
        _reason(
            EligibilityReasonCode.GRADUATION_YEAR_NOT_ALLOWED,
            expected=", ".join(str(year) for year in allowed_years),
            actual=str(profile.graduation_year),
        ),
    ]


def _check_active_backlogs(
    rule: EligibilityRule,
    academic: StudentAcademicInformation | None,
) -> list[EligibilityReason]:
    if rule.maximum_active_backlogs is None:
        return []

    expected = f"<= {rule.maximum_active_backlogs}"

    if academic is None:
        return [
            _reason(
                EligibilityReasonCode.ACADEMIC_INFO_MISSING,
                expected=f"Active backlogs {expected}",
                actual="Academic information not provided",
            ),
        ]

    if academic.active_backlogs > rule.maximum_active_backlogs:
        return [
            _reason(
                EligibilityReasonCode.ACTIVE_BACKLOGS_EXCEEDED,
                expected=expected,
                actual=str(academic.active_backlogs),
            ),
        ]
    return []


def _check_backlog_history(
    rule: EligibilityRule,
    academic: StudentAcademicInformation | None,
) -> list[EligibilityReason]:
    if rule.allow_backlog_history:
        return []

    if academic is None:
        return [
            _reason(
                EligibilityReasonCode.ACADEMIC_INFO_MISSING,
                expected="No backlog history",
                actual="Academic information not provided",
            ),
        ]

    if academic.total_history_backlogs > 0:
        return [
            _reason(
                EligibilityReasonCode.BACKLOG_HISTORY_NOT_ALLOWED,
                expected="0",
                actual=str(academic.total_history_backlogs),
            ),
        ]
    return []


def _check_gender(
    rule: EligibilityRule,
    personal: StudentPersonalInformation | None,
) -> list[EligibilityReason]:
    if not rule.gender_restriction:
        return []

    expected = rule.gender_restriction

    if personal is None:
        return [
            _reason(
                EligibilityReasonCode.PERSONAL_INFO_MISSING,
                expected=f"Gender = {expected}",
                actual="Personal information not provided",
            ),
        ]

    actual = personal.gender.value if hasattr(personal.gender, "value") else str(personal.gender)
    if actual.lower() != expected.lower():
        return [
            _reason(
                EligibilityReasonCode.GENDER_RESTRICTED,
                expected=expected,
                actual=actual,
            ),
        ]
    return []


def _check_education_requirements(
    rule: EligibilityRule,
    education_history: list[StudentEducationHistory],
) -> list[EligibilityReason]:
    """
    Evaluate only documented, deterministic education_requirements keys.

    Supported keys:
      - required_education_types: list[str]
      - minimum_secondary_percentage
      - minimum_higher_secondary_percentage
      - minimum_diploma_percentage
      - minimum_undergraduate_percentage

    Unknown keys are ignored (no heuristics).
    """
    requirements = rule.education_requirements
    if not requirements or not isinstance(requirements, dict):
        return []

    reasons: list[EligibilityReason] = []
    by_type = {
        entry.education_type.value: entry for entry in education_history
    }

    required_types = requirements.get("required_education_types")
    if isinstance(required_types, list):
        for education_type in required_types:
            type_key = str(education_type)
            if type_key not in by_type:
                reasons.append(
                    _reason(
                        EligibilityReasonCode.EDUCATION_TYPE_MISSING,
                        expected=type_key,
                        actual="Not provided",
                    ),
                )

    for key, education_type in EDUCATION_MIN_SCORE_KEYS.items():
        if key not in requirements:
            continue
        minimum = _parse_decimal(requirements[key])
        if minimum is None:
            continue

        entry = by_type.get(education_type)
        if entry is None:
            reasons.append(
                _reason(
                    EligibilityReasonCode.EDUCATION_TYPE_MISSING,
                    expected=f"{education_type} score >= {_format_decimal(minimum)}",
                    actual="Not provided",
                ),
            )
            continue

        actual = _parse_decimal(entry.percentage_or_cgpa)
        if actual is None or actual < minimum:
            reasons.append(
                _reason(
                    EligibilityReasonCode.EDUCATION_SCORE_BELOW_MINIMUM,
                    expected=f"{education_type} >= {_format_decimal(minimum)}",
                    actual=str(entry.percentage_or_cgpa),
                ),
            )

    return reasons


def is_eligible(reasons: list[EligibilityReason]) -> bool:
    return len(reasons) == 0
