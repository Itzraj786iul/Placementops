import uuid
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from app.modules.students.completion import (
    calculate_profile_completion,
    get_profile_requirements,
)
from app.modules.students.enums import DocumentType, Gender, ProfileStatus, EducationType
from app.modules.students.exceptions import StudentValidationError
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
from app.modules.students.schemas import StudentProfileCreate, StudentProfileUpdate
from app.modules.students.service import StudentService


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
    missing, completed, total = get_profile_requirements(profile)
    assert missing == []
    assert completed == total
    assert total == 10


def test_missing_requirements_lists_gaps() -> None:
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
    profile.personal_information = None
    profile.academic_information = None
    profile.education_history = []
    profile.resumes = []
    profile.documents = []
    profile.skills = []
    profile.projects = []

    missing, completed, total = get_profile_requirements(profile)
    assert completed == 1  # institute details only
    assert total == 10
    codes = {item["code"] for item in missing}
    assert "PERSONAL" in codes
    assert "RESUME" in codes
    assert "AADHAR" in codes
    assert "PROJECT" in codes


def _student_actor(user_id: uuid.UUID | None = None) -> SimpleNamespace:
    return SimpleNamespace(
        id=user_id or uuid.uuid4(),
        roles=[SimpleNamespace(name="STUDENT")],
    )


def _complete_profile(
    *,
    user_id: uuid.UUID,
    status: ProfileStatus = ProfileStatus.DRAFT,
    completion: int = 100,
) -> StudentProfile:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    profile_id = uuid.uuid4()
    department = Department(id=uuid.uuid4(), name="CSE", code="CSE")
    profile = StudentProfile(
        id=profile_id,
        user_id=user_id,
        department_id=department.id,
        department=department,
        roll_number="ROLL001",
        registration_number="REG001",
        graduation_year=2026,
        profile_status=status,
        profile_completion=completion,
        created_at=now,
        updated_at=now,
    )
    profile.personal_information = StudentPersonalInformation(
        student_profile_id=profile_id,
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
        student_profile_id=profile_id,
        current_cgpa=Decimal("8.50"),
        active_backlogs=0,
        total_history_backlogs=0,
        semester=6,
    )
    profile.education_history = [
        StudentEducationHistory(
            id=uuid.uuid4(),
            student_profile_id=profile_id,
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
            student_profile_id=profile_id,
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
            student_profile_id=profile_id,
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
            id=uuid.uuid4(),
            student_profile_id=profile_id,
            skill_name="Python",
            skill_level="Advanced",
        ),
    ]
    profile.projects = [
        StudentProject(
            id=uuid.uuid4(),
            student_profile_id=profile_id,
            title="Project",
            description="Desc",
            tech_stack="Python",
            github_url=None,
            demo_url=None,
        ),
    ]
    return profile


def test_submit_my_profile_draft_to_submitted() -> None:
    user = _student_actor()
    profile = _complete_profile(user_id=user.id, status=ProfileStatus.DRAFT)

    db = MagicMock()
    service = StudentService(db)
    service.repository = MagicMock()
    service.repository.get_profile_by_user_id.return_value = profile
    service.repository.get_profile_by_id.return_value = profile

    with (
        patch("app.modules.students.service.record_audit"),
        patch(
            "app.platform.notifications.triggers.notify_profile_submitted",
        ) as notify,
    ):
        result = service.submit_my_profile(user)

    assert profile.profile_status == ProfileStatus.SUBMITTED
    assert result.profile_status == ProfileStatus.SUBMITTED
    notify.assert_called_once()
    db.commit.assert_called_once()


def test_submit_my_profile_rejected_to_submitted() -> None:
    user = _student_actor()
    profile = _complete_profile(user_id=user.id, status=ProfileStatus.REJECTED)

    db = MagicMock()
    service = StudentService(db)
    service.repository = MagicMock()
    service.repository.get_profile_by_user_id.return_value = profile
    service.repository.get_profile_by_id.return_value = profile

    with (
        patch("app.modules.students.service.record_audit"),
        patch("app.platform.notifications.triggers.notify_profile_submitted"),
    ):
        service.submit_my_profile(user)

    assert profile.profile_status == ProfileStatus.SUBMITTED


def test_submit_my_profile_requires_100_percent() -> None:
    user = _student_actor()
    profile = _complete_profile(
        user_id=user.id,
        status=ProfileStatus.DRAFT,
        completion=80,
    )
    profile.projects = []

    db = MagicMock()
    service = StudentService(db)
    service.repository = MagicMock()
    service.repository.get_profile_by_user_id.return_value = profile
    service.repository.get_profile_by_id.return_value = profile

    with pytest.raises(StudentValidationError, match="100%"):
        service.submit_my_profile(user)


def test_submit_my_profile_rejects_non_draft_rejected() -> None:
    user = _student_actor()
    profile = _complete_profile(
        user_id=user.id,
        status=ProfileStatus.UNDER_REVIEW,
    )

    db = MagicMock()
    service = StudentService(db)
    service.repository = MagicMock()
    service.repository.get_profile_by_user_id.return_value = profile
    service.repository.get_profile_by_id.return_value = profile

    with pytest.raises(StudentValidationError, match="draft or rejected"):
        service.submit_my_profile(user)


def test_student_cannot_patch_profile_status() -> None:
    user = _student_actor()
    profile = _complete_profile(user_id=user.id, status=ProfileStatus.DRAFT)

    db = MagicMock()
    service = StudentService(db)
    service.repository = MagicMock()
    service.repository.get_profile_by_id.return_value = profile

    with pytest.raises(StudentValidationError, match="Only staff"):
        service.update_profile(
            user,
            profile.id,
            StudentProfileUpdate(profile_status=ProfileStatus.SUBMITTED),
        )
