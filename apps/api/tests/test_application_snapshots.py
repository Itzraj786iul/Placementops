import uuid
from datetime import date
from decimal import Decimal

from app.modules.applications.snapshots import (
    build_eligibility_snapshot,
    build_profile_snapshot,
    build_resume_snapshot,
)
from app.modules.hiring_opportunities.models import EligibilityRule
from app.modules.students.enums import Gender, ProfileStatus
from app.modules.students.models import (
    Department,
    StudentAcademicInformation,
    StudentPersonalInformation,
    StudentProfile,
    StudentResumeLibrary,
)


def test_build_resume_snapshot() -> None:
    resume_id = uuid.uuid4()
    profile_id = uuid.uuid4()
    resume = StudentResumeLibrary(
        id=resume_id,
        student_profile_id=profile_id,
        name="Primary Resume",
        file_url="https://example.com/resume.pdf",
        version=2,
        is_active=True,
    )
    snapshot = build_resume_snapshot(resume)
    assert snapshot["id"] == str(resume_id)
    assert snapshot["name"] == "Primary Resume"
    assert snapshot["is_active"] is True


def test_build_eligibility_snapshot_empty_when_missing() -> None:
    assert build_eligibility_snapshot(None) == {}


def test_build_profile_snapshot_includes_core_fields() -> None:
    department = Department(id=uuid.uuid4(), name="CSE", code="CSE")
    profile = StudentProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        department_id=department.id,
        department=department,
        roll_number="2021CS001",
        registration_number="REG001",
        graduation_year=2025,
        profile_status=ProfileStatus.DRAFT,
        profile_completion=80,
    )
    profile.personal_information = StudentPersonalInformation(
        student_profile_id=profile.id,
        first_name="Demo",
        last_name="Student",
        gender=Gender.MALE,
        date_of_birth=date(2002, 1, 1),
        phone_number="9999999999",
        alternate_phone=None,
        personal_email="demo@example.com",
        address="Campus",
        city="Raipur",
        state="CG",
        country="India",
        photo_url=None,
    )
    profile.academic_information = StudentAcademicInformation(
        student_profile_id=profile.id,
        current_cgpa=Decimal("8.50"),
        active_backlogs=0,
        total_history_backlogs=0,
        semester=7,
    )
    profile.skills = []
    profile.projects = []

    snapshot = build_profile_snapshot(profile)
    assert snapshot["roll_number"] == "2021CS001"
    assert snapshot["department_code"] == "CSE"
    assert snapshot["academic_information"]["current_cgpa"] == "8.50"

    rule = EligibilityRule(
        id=uuid.uuid4(),
        hiring_opportunity_id=uuid.uuid4(),
        minimum_cgpa=Decimal("7.00"),
        allowed_departments=[str(department.id)],
        allowed_graduation_years=[2025],
        maximum_active_backlogs=0,
        allow_backlog_history=True,
        gender_restriction=None,
        education_requirements=None,
    )
    eligibility = build_eligibility_snapshot(rule)
    assert eligibility["minimum_cgpa"] == "7.00"
