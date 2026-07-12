from __future__ import annotations

from dataclasses import dataclass

from app.modules.students.enums import DocumentType
from app.modules.students.models import StudentProfile
from app.modules.students.schemas import PROFILE_COMPLETION_WEIGHTS

REQUIRED_DOCUMENT_TYPES = {
    DocumentType.AADHAR,
    DocumentType.TENTH_MARKSHEET,
    DocumentType.TWELFTH_MARKSHEET,
}

DOCUMENT_REQUIREMENT_LABELS: dict[DocumentType, str] = {
    DocumentType.AADHAR: "Upload Aadhar Card",
    DocumentType.TENTH_MARKSHEET: "Upload 10th Marksheet",
    DocumentType.TWELFTH_MARKSHEET: "Upload 12th Marksheet",
}

DOCUMENT_REQUIREMENT_CODES: dict[DocumentType, str] = {
    DocumentType.AADHAR: "AADHAR",
    DocumentType.TENTH_MARKSHEET: "TENTH_MARKSHEET",
    DocumentType.TWELFTH_MARKSHEET: "TWELFTH_MARKSHEET",
}


@dataclass(frozen=True)
class RequirementSpec:
    code: str
    label: str
    step: str
    focus: str
    estimated_minutes: int
    done: bool


def calculate_profile_completion(profile: StudentProfile) -> int:
    completion = 0

    if all(
        [
            profile.department_id,
            profile.roll_number,
            profile.registration_number,
            profile.graduation_year,
        ],
    ):
        completion += PROFILE_COMPLETION_WEIGHTS["core"]

    if profile.personal_information is not None:
        completion += PROFILE_COMPLETION_WEIGHTS["personal"]

    if profile.academic_information is not None:
        completion += PROFILE_COMPLETION_WEIGHTS["academic"]

    if profile.education_history:
        completion += PROFILE_COMPLETION_WEIGHTS["education"]

    if profile.resumes:
        completion += PROFILE_COMPLETION_WEIGHTS["resume"]

    uploaded_types = {document.document_type for document in profile.documents}
    if REQUIRED_DOCUMENT_TYPES.issubset(uploaded_types):
        completion += PROFILE_COMPLETION_WEIGHTS["documents"]

    if profile.skills:
        completion += PROFILE_COMPLETION_WEIGHTS["skills"]

    if profile.projects:
        completion += PROFILE_COMPLETION_WEIGHTS["projects"]

    return min(completion, 100)


def _required_specs(profile: StudentProfile) -> list[RequirementSpec]:
    uploaded_types = {document.document_type for document in profile.documents}
    core_ok = all(
        [
            profile.department_id,
            profile.roll_number,
            profile.registration_number,
            profile.graduation_year,
        ],
    )

    specs: list[RequirementSpec] = [
        RequirementSpec(
            code="CORE",
            label="Complete institute details",
            step="personal",
            focus="core",
            estimated_minutes=1,
            done=core_ok,
        ),
        RequirementSpec(
            code="PERSONAL",
            label="Complete Personal Information",
            step="personal",
            focus="personal-section",
            estimated_minutes=3,
            done=profile.personal_information is not None,
        ),
        RequirementSpec(
            code="ACADEMIC",
            label="Complete Academic Information",
            step="academic",
            focus="academic-section",
            estimated_minutes=2,
            done=profile.academic_information is not None,
        ),
        RequirementSpec(
            code="EDUCATION",
            label="Add Education History",
            step="education",
            focus="education-section",
            estimated_minutes=3,
            done=bool(profile.education_history),
        ),
        RequirementSpec(
            code="RESUME",
            label="Upload a Resume",
            step="resume",
            focus="resume-section",
            estimated_minutes=2,
            done=bool(profile.resumes),
        ),
    ]

    for doc_type in (
        DocumentType.AADHAR,
        DocumentType.TENTH_MARKSHEET,
        DocumentType.TWELFTH_MARKSHEET,
    ):
        specs.append(
            RequirementSpec(
                code=DOCUMENT_REQUIREMENT_CODES[doc_type],
                label=DOCUMENT_REQUIREMENT_LABELS[doc_type],
                step="documents",
                focus=f"document-{doc_type.value}",
                estimated_minutes=1,
                done=doc_type in uploaded_types,
            ),
        )

    specs.extend(
        [
            RequirementSpec(
                code="SKILL",
                label="Add at least one Skill",
                step="skills",
                focus="skills-section",
                estimated_minutes=1,
                done=bool(profile.skills),
            ),
            RequirementSpec(
                code="PROJECT",
                label="Add at least one Project",
                step="projects",
                focus="projects-section",
                estimated_minutes=3,
                done=bool(profile.projects),
            ),
        ],
    )
    return specs


def _optional_specs(profile: StudentProfile) -> list[RequirementSpec]:
    personal = profile.personal_information
    uploaded_types = {document.document_type for document in profile.documents}
    has_active_resume = any(resume.is_active for resume in profile.resumes)
    has_github = any(project.github_url for project in profile.projects)
    has_demo = any(project.demo_url for project in profile.projects)

    return [
        RequirementSpec(
            code="PHOTO",
            label="Upload profile photo",
            step="personal",
            focus="photo_upload",
            estimated_minutes=1,
            done=bool(personal and personal.photo_url),
        ),
        RequirementSpec(
            code="ALTERNATE_PHONE",
            label="Add alternate phone",
            step="personal",
            focus="alternate_phone",
            estimated_minutes=1,
            done=bool(personal and personal.alternate_phone),
        ),
        RequirementSpec(
            code="PERSONAL_EMAIL",
            label="Add personal email",
            step="personal",
            focus="personal_email",
            estimated_minutes=1,
            done=bool(personal and personal.personal_email),
        ),
        RequirementSpec(
            code="PAN",
            label="Upload PAN Card",
            step="documents",
            focus="document-PAN",
            estimated_minutes=1,
            done=DocumentType.PAN in uploaded_types,
        ),
        RequirementSpec(
            code="SEMESTER_MARKSHEET",
            label="Upload Semester Marksheet",
            step="documents",
            focus="document-SEMESTER_MARKSHEET",
            estimated_minutes=1,
            done=DocumentType.SEMESTER_MARKSHEET in uploaded_types,
        ),
        RequirementSpec(
            code="OTHER_DOCUMENT",
            label="Upload additional document",
            step="documents",
            focus="document-OTHER",
            estimated_minutes=1,
            done=DocumentType.OTHER in uploaded_types,
        ),
        RequirementSpec(
            code="RESUME_ACTIVE",
            label="Activate a Resume",
            step="resume",
            focus="resume-section",
            estimated_minutes=1,
            done=has_active_resume,
        ),
        RequirementSpec(
            code="PROJECT_GITHUB",
            label="Add a project GitHub link",
            step="projects",
            focus="projects-section",
            estimated_minutes=1,
            done=has_github,
        ),
        RequirementSpec(
            code="PROJECT_DEMO",
            label="Add a project demo link",
            step="projects",
            focus="projects-section",
            estimated_minutes=1,
            done=has_demo,
        ),
        RequirementSpec(
            code="SKILLS_EXTRA",
            label="Add at least 3 skills",
            step="skills",
            focus="skills-section",
            estimated_minutes=1,
            done=len(profile.skills or []) >= 3,
        ),
    ]


def get_profile_requirements(
    profile: StudentProfile,
) -> tuple[list[dict[str, str | int]], int, int]:
    """Return (missing requirement dicts, completed count, total count)."""
    specs = _required_specs(profile)
    missing = [
        {
            "code": spec.code,
            "label": spec.label,
            "step": spec.step,
            "focus": spec.focus,
            "estimated_minutes": spec.estimated_minutes,
        }
        for spec in specs
        if not spec.done
    ]
    completed = sum(1 for spec in specs if spec.done)
    return missing, completed, len(specs)


def get_optional_requirements(
    profile: StudentProfile,
) -> tuple[list[dict[str, str | int]], int, int]:
    specs = _optional_specs(profile)
    missing = [
        {
            "code": spec.code,
            "label": spec.label,
            "step": spec.step,
            "focus": spec.focus,
            "estimated_minutes": spec.estimated_minutes,
        }
        for spec in specs
        if not spec.done
    ]
    completed = sum(1 for spec in specs if spec.done)
    return missing, completed, len(specs)


def get_profile_completion_guide(profile: StudentProfile) -> dict:
    missing, completed, total = get_profile_requirements(profile)
    optional_missing, optional_completed, optional_total = get_optional_requirements(
        profile,
    )
    estimated = sum(int(item["estimated_minutes"]) for item in missing)
    return {
        "missing_requirements": missing,
        "requirements_completed": completed,
        "requirements_total": total,
        "optional_completed": optional_completed,
        "optional_total": optional_total,
        "optional_missing": optional_missing,
        "estimated_minutes_remaining": estimated,
    }
