import uuid
from datetime import date
from decimal import Decimal

import pytest

from app.modules.students.completion import calculate_profile_completion
from app.modules.students.enums import DocumentType, Gender, ProfileStatus, EducationType
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
from app.modules.students.schemas import StudentProfileCreate


def test_profile_create_schema_validation() -> None:
    with pytest.raises(ValueError):
        StudentProfileCreate(
            department_id=uuid.uuid4(),
            roll_number="   ",
            registration_number="REG001",
            graduation_year=2026,
        )


def test_profile_completion_weights() -> None:
    department = Department(id=uuid.uuid4(), name="CSE", code="CSE")
    profile = StudentProfile(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        department_id=department.id,
        department=department,
        roll_number="ROLL001",
        registration_number="REG001",
        graduation_year=2026,
        profile_status=ProfileStatus.DRAFT,
        profile_completion=0,
    )
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
            id=uuid.uuid4(),
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
            id=uuid.uuid4(),
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
            id=uuid.uuid4(),
            student_profile_id=profile.id,
            document_type=doc_type,
            file_url="https://example.com/doc.pdf",
            file_name="doc.pdf",
            status="PENDING",
        )
        for doc_type in [
            DocumentType.PHOTO,
            DocumentType.AADHAR,
            DocumentType.TENTH_MARKSHEET,
            DocumentType.TWELFTH_MARKSHEET,
        ]
    ]
    profile.skills = [
        StudentSkill(
            id=uuid.uuid4(),
            student_profile_id=profile.id,
            skill_name="Python",
            skill_level="Advanced",
        ),
    ]
    profile.projects = [
        StudentProject(
            id=uuid.uuid4(),
            student_profile_id=profile.id,
            title="Project",
            description="Desc",
            tech_stack="Python",
            github_url=None,
            demo_url=None,
        ),
    ]

    assert calculate_profile_completion(profile) == 100
