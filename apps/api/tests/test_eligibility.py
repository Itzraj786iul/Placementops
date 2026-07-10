import uuid
from datetime import date
from decimal import Decimal

from app.modules.eligibility.enums import EligibilityReasonCode
from app.modules.eligibility.evaluator import evaluate_student, is_eligible
from app.modules.hiring_opportunities.models import EligibilityRule
from app.modules.students.enums import EducationType, Gender, ProfileStatus
from app.modules.students.models import (
    Department,
    StudentAcademicInformation,
    StudentEducationHistory,
    StudentPersonalInformation,
    StudentProfile,
)


def _department() -> Department:
    return Department(id=uuid.uuid4(), name="Computer Science", code="CSE")


def _profile(
    *,
    department: Department | None = None,
    graduation_year: int = 2026,
    cgpa: str = "8.50",
    active_backlogs: int = 0,
    history_backlogs: int = 0,
    gender: Gender = Gender.MALE,
    with_academic: bool = True,
    with_personal: bool = True,
    education: list[StudentEducationHistory] | None = None,
) -> StudentProfile:
    dept = department or _department()
    profile = StudentProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        department_id=dept.id,
        department=dept,
        roll_number="2022CS001",
        registration_number="REG001",
        graduation_year=graduation_year,
        profile_status=ProfileStatus.VERIFIED,
        profile_completion=100,
    )
    if with_personal:
        profile.personal_information = StudentPersonalInformation(
            student_profile_id=profile.id,
            first_name="Ada",
            last_name="Student",
            gender=gender,
            date_of_birth=date(2003, 5, 1),
            phone_number="9999999999",
            alternate_phone=None,
            personal_email="ada@example.com",
            address="Campus",
            city="Raipur",
            state="CG",
            country="India",
            photo_url=None,
        )
    else:
        profile.personal_information = None

    if with_academic:
        profile.academic_information = StudentAcademicInformation(
            student_profile_id=profile.id,
            current_cgpa=Decimal(cgpa),
            active_backlogs=active_backlogs,
            total_history_backlogs=history_backlogs,
            semester=6,
        )
    else:
        profile.academic_information = None

    profile.education_history = education or []
    return profile


def _rule(**overrides) -> EligibilityRule:
    rule = EligibilityRule(
        id=uuid.uuid4(),
        hiring_opportunity_id=uuid.uuid4(),
        minimum_cgpa=None,
        allowed_departments=None,
        allowed_graduation_years=None,
        maximum_active_backlogs=None,
        allow_backlog_history=True,
        gender_restriction=None,
        education_requirements=None,
    )
    for key, value in overrides.items():
        setattr(rule, key, value)
    return rule


def test_perfect_eligibility() -> None:
    profile = _profile()
    rule = _rule(
        minimum_cgpa=Decimal("7.00"),
        maximum_active_backlogs=0,
        allow_backlog_history=True,
    )
    reasons = evaluate_student(rule, profile)
    assert is_eligible(reasons)
    assert reasons == []


def test_no_rule_means_eligible() -> None:
    profile = _profile()
    reasons = evaluate_student(None, profile)
    assert is_eligible(reasons)


def test_missing_profile() -> None:
    reasons = evaluate_student(_rule(), None)
    assert not is_eligible(reasons)
    assert reasons[0].code == EligibilityReasonCode.PROFILE_MISSING


def test_cgpa_below_minimum() -> None:
    profile = _profile(cgpa="6.20")
    rule = _rule(minimum_cgpa=Decimal("7.00"))
    reasons = evaluate_student(rule, profile)
    assert not is_eligible(reasons)
    assert reasons[0].code == EligibilityReasonCode.CGPA_BELOW_MINIMUM
    assert reasons[0].expected == ">= 7.00"
    assert reasons[0].actual == "6.20"


def test_cgpa_missing_academic() -> None:
    profile = _profile(with_academic=False)
    rule = _rule(minimum_cgpa=Decimal("7.00"))
    reasons = evaluate_student(rule, profile)
    assert any(r.code == EligibilityReasonCode.ACADEMIC_INFO_MISSING for r in reasons)


def test_department_not_allowed() -> None:
    cse = _department()
    ece = Department(id=uuid.uuid4(), name="Electronics", code="ECE")
    profile = _profile(department=cse)
    rule = _rule(allowed_departments=[str(ece.id)])
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED
    assert reasons[0].actual == "Computer Science"


def test_department_allowed() -> None:
    cse = _department()
    profile = _profile(department=cse)
    rule = _rule(allowed_departments=[str(cse.id)])
    assert is_eligible(evaluate_student(rule, profile))


def test_graduation_year_not_allowed() -> None:
    profile = _profile(graduation_year=2027)
    rule = _rule(allowed_graduation_years=[2025, 2026])
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.GRADUATION_YEAR_NOT_ALLOWED
    assert reasons[0].actual == "2027"
    assert "2025" in reasons[0].expected


def test_active_backlogs_exceeded() -> None:
    profile = _profile(active_backlogs=2)
    rule = _rule(maximum_active_backlogs=0)
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.ACTIVE_BACKLOGS_EXCEEDED
    assert reasons[0].actual == "2"


def test_backlog_history_not_allowed() -> None:
    profile = _profile(history_backlogs=3)
    rule = _rule(allow_backlog_history=False)
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.BACKLOG_HISTORY_NOT_ALLOWED
    assert reasons[0].actual == "3"


def test_gender_restricted() -> None:
    profile = _profile(gender=Gender.MALE)
    rule = _rule(gender_restriction="FEMALE")
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.GENDER_RESTRICTED
    assert reasons[0].expected == "FEMALE"
    assert reasons[0].actual == "MALE"


def test_gender_case_insensitive_match() -> None:
    profile = _profile(gender=Gender.FEMALE)
    rule = _rule(gender_restriction="female")
    assert is_eligible(evaluate_student(rule, profile))


def test_gender_missing_personal() -> None:
    profile = _profile(with_personal=False)
    rule = _rule(gender_restriction="FEMALE")
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.PERSONAL_INFO_MISSING


def test_multiple_failures_all_returned() -> None:
    cse = _department()
    other = Department(id=uuid.uuid4(), name="Mechanical", code="ME")
    profile = _profile(
        department=cse,
        cgpa="5.00",
        graduation_year=2028,
        active_backlogs=2,
        history_backlogs=1,
        gender=Gender.MALE,
    )
    rule = _rule(
        minimum_cgpa=Decimal("7.50"),
        allowed_departments=[str(other.id)],
        allowed_graduation_years=[2026],
        maximum_active_backlogs=0,
        allow_backlog_history=False,
        gender_restriction="FEMALE",
    )
    reasons = evaluate_student(rule, profile)
    codes = {r.code for r in reasons}
    assert EligibilityReasonCode.CGPA_BELOW_MINIMUM in codes
    assert EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED in codes
    assert EligibilityReasonCode.GRADUATION_YEAR_NOT_ALLOWED in codes
    assert EligibilityReasonCode.ACTIVE_BACKLOGS_EXCEEDED in codes
    assert EligibilityReasonCode.BACKLOG_HISTORY_NOT_ALLOWED in codes
    assert EligibilityReasonCode.GENDER_RESTRICTED in codes
    assert len(reasons) == 6


def test_education_required_type_missing() -> None:
    profile = _profile(education=[])
    rule = _rule(
        education_requirements={"required_education_types": ["HIGHER_SECONDARY"]},
    )
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.EDUCATION_TYPE_MISSING


def test_education_score_below_minimum() -> None:
    profile_id = uuid.uuid4()
    education = [
        StudentEducationHistory(
            id=uuid.uuid4(),
            student_profile_id=profile_id,
            education_type=EducationType.HIGHER_SECONDARY,
            institution="School",
            board="CBSE",
            passing_year=2020,
            percentage_or_cgpa="55.0",
        ),
    ]
    profile = _profile(education=education)
    profile.id = profile_id
    rule = _rule(
        education_requirements={"minimum_higher_secondary_percentage": 60},
    )
    reasons = evaluate_student(rule, profile)
    assert reasons[0].code == EligibilityReasonCode.EDUCATION_SCORE_BELOW_MINIMUM


def test_education_score_meets_minimum() -> None:
    profile_id = uuid.uuid4()
    education = [
        StudentEducationHistory(
            id=uuid.uuid4(),
            student_profile_id=profile_id,
            education_type=EducationType.HIGHER_SECONDARY,
            institution="School",
            board="CBSE",
            passing_year=2020,
            percentage_or_cgpa="72.5",
        ),
    ]
    profile = _profile(education=education)
    profile.id = profile_id
    rule = _rule(
        education_requirements={"minimum_higher_secondary_percentage": 60},
    )
    assert is_eligible(evaluate_student(rule, profile))


def test_unknown_education_keys_ignored() -> None:
    profile = _profile()
    rule = _rule(education_requirements={"mystery_heuristic": True})
    assert is_eligible(evaluate_student(rule, profile))


def test_screening_aggregation() -> None:
    from app.modules.eligibility.enums import REASON_TITLES
    from app.modules.eligibility.schemas import EligibilityReason
    from app.modules.eligibility.screening import aggregate_screening

    opportunity_id = uuid.uuid4()
    cgpa_reason = EligibilityReason(
        code=EligibilityReasonCode.CGPA_BELOW_MINIMUM,
        title=REASON_TITLES[EligibilityReasonCode.CGPA_BELOW_MINIMUM],
        expected=">= 7.00",
        actual="6.00",
    )
    dept_reason = EligibilityReason(
        code=EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED,
        title=REASON_TITLES[EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED],
        expected="CSE",
        actual="ME",
    )

    summary = aggregate_screening(
        opportunity_id,
        [
            [],
            [],
            [cgpa_reason],
            [cgpa_reason, dept_reason],
            [dept_reason],
        ],
    )
    assert summary.total_applications == 5
    assert summary.eligible_count == 2
    assert summary.ineligible_count == 3
    by_code = {item.code: item.count for item in summary.reason_breakdown}
    assert by_code[EligibilityReasonCode.CGPA_BELOW_MINIMUM] == 2
    assert by_code[EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED] == 2
