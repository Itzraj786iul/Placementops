"""Unit tests for profile completion guide (no DB)."""

from datetime import date
from decimal import Decimal
from uuid import uuid4

from app.modules.students.completion import (
    calculate_profile_completion,
    get_profile_completion_guide,
    get_profile_requirements,
)
from app.modules.students.enums import DocumentType, EducationType, Gender, ProfileStatus
from app.modules.students.models import (
    Department,
    StudentAcademicInformation,
    StudentDocument,
    StudentEducationHistory,
    StudentPersonalInformation,
    StudentProfile,
    StudentProject,
    StudentResumeLibrary,
    StudentSkill,
)


def _base_profile() -> StudentProfile:
    department = Department(id=uuid4(), name="CSE", code="CSE")
    return StudentProfile(
        id=uuid4(),
        user_id=uuid4(),
        department_id=department.id,
        department=department,
        roll_number="ROLL001",
        registration_number="REG001",
        graduation_year=2026,
        profile_status=ProfileStatus.DRAFT,
        profile_completion=0,
    )


def test_missing_requirements_are_actionable() -> None:
    profile = _base_profile()
    profile.personal_information = None
    profile.academic_information = None
    profile.education_history = []
    profile.resumes = []
    profile.documents = []
    profile.skills = []
    profile.projects = []

    missing, completed, total = get_profile_requirements(profile)
    assert completed == 1
    assert total == 10
    codes = {item["code"] for item in missing}
    assert "PERSONAL" in codes
    assert "AADHAR" in codes
    assert "PROJECT" in codes
    personal = next(item for item in missing if item["code"] == "PERSONAL")
    assert personal["step"] == "personal"
    assert personal["focus"] == "personal-section"


def test_completion_guide_includes_optional_counts() -> None:
    profile = _base_profile()
    profile.personal_information = None
    profile.academic_information = None
    profile.education_history = []
    profile.resumes = []
    profile.documents = []
    profile.skills = []
    profile.projects = []

    guide = get_profile_completion_guide(profile)
    assert guide["requirements_completed"] == 1
    assert guide["requirements_total"] == 10
    assert guide["optional_total"] == 10
    assert guide["optional_completed"] == 0
    assert guide["estimated_minutes_remaining"] > 0
    assert all("step" in item for item in guide["missing_requirements"])


def test_complete_profile_has_no_missing() -> None:
    profile = _base_profile()
    profile.personal_information = StudentPersonalInformation(
        student_profile_id=profile.id,
        first_name="A",
        last_name="B",
        gender=Gender.MALE,
        date_of_birth=date(2000, 1, 1),
        phone_number="9999999999",
        alternate_phone=None,
        personal_email=None,
        address="Addr",
        city="City",
        state="State",
        country="India",
        photo_url=None,
    )
    profile.academic_information = StudentAcademicInformation(
        student_profile_id=profile.id,
        current_cgpa=Decimal("8.50"),
        active_backlogs=0,
        total_history_backlogs=0,
        semester=6,
    )
    profile.education_history = [
        StudentEducationHistory(
            id=uuid4(),
            student_profile_id=profile.id,
            education_type=EducationType.SECONDARY,
            institution="School",
            board="CBSE",
            passing_year=2018,
            percentage_or_cgpa="90",
        ),
    ]
    profile.resumes = [
        StudentResumeLibrary(
            id=uuid4(),
            student_profile_id=profile.id,
            name="Resume",
            file_url="https://example.com/r.pdf",
            version=1,
            is_active=True,
            last_used=None,
        ),
    ]
    profile.documents = [
        StudentDocument(
            id=uuid4(),
            student_profile_id=profile.id,
            document_type=doc_type,
            file_url="https://example.com/doc.pdf",
            file_name="doc.pdf",
            status="PENDING",
        )
        for doc_type in [
            DocumentType.AADHAR,
            DocumentType.TENTH_MARKSHEET,
            DocumentType.TWELFTH_MARKSHEET,
        ]
    ]
    profile.skills = [
        StudentSkill(
            id=uuid4(),
            student_profile_id=profile.id,
            skill_name="Python",
            skill_level="Advanced",
        ),
    ]
    profile.projects = [
        StudentProject(
            id=uuid4(),
            student_profile_id=profile.id,
            title="Project",
            description="Desc",
            tech_stack="Python",
            github_url=None,
            demo_url=None,
        ),
    ]

    assert calculate_profile_completion(profile) == 100
    missing, completed, total = get_profile_requirements(profile)
    assert missing == []
    assert completed == total == 10
