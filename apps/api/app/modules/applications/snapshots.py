from __future__ import annotations

from decimal import Decimal

from app.modules.hiring_opportunities.models import EligibilityRule
from app.modules.students.models import (
    StudentAcademicInformation,
    StudentPersonalInformation,
    StudentProfile,
    StudentResumeLibrary,
)


def _serialize_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    return str(value)


def build_profile_snapshot(profile: StudentProfile) -> dict:
    personal: StudentPersonalInformation | None = profile.personal_information
    academic: StudentAcademicInformation | None = profile.academic_information

    return {
        "id": str(profile.id),
        "user_id": str(profile.user_id),
        "department_id": str(profile.department_id),
        "department_name": profile.department.name if profile.department else None,
        "department_code": profile.department.code if profile.department else None,
        "roll_number": profile.roll_number,
        "registration_number": profile.registration_number,
        "graduation_year": profile.graduation_year,
        "profile_status": profile.profile_status.value,
        "profile_completion": profile.profile_completion,
        "personal_information": {
            "first_name": personal.first_name,
            "last_name": personal.last_name,
            "gender": personal.gender.value,
            "date_of_birth": personal.date_of_birth.isoformat(),
            "phone_number": personal.phone_number,
            "alternate_phone": personal.alternate_phone,
            "personal_email": personal.personal_email,
            "address": personal.address,
            "city": personal.city,
            "state": personal.state,
            "country": personal.country,
            "photo_url": personal.photo_url,
        }
        if personal
        else None,
        "academic_information": {
            "current_cgpa": _serialize_decimal(academic.current_cgpa),
            "active_backlogs": academic.active_backlogs,
            "total_history_backlogs": academic.total_history_backlogs,
            "semester": academic.semester,
        }
        if academic
        else None,
        "skills": [
            {"skill_name": skill.skill_name, "skill_level": skill.skill_level}
            for skill in profile.skills
        ],
        "projects": [
            {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "github_url": project.github_url,
                "demo_url": project.demo_url,
            }
            for project in profile.projects
        ],
    }


def build_resume_snapshot(resume: StudentResumeLibrary) -> dict:
    return {
        "id": str(resume.id),
        "student_profile_id": str(resume.student_profile_id),
        "name": resume.name,
        "file_url": resume.file_url,
        "version": resume.version,
        "is_active": resume.is_active,
        "uploaded_at": resume.uploaded_at.isoformat() if resume.uploaded_at else None,
    }


def build_eligibility_snapshot(rule: EligibilityRule | None) -> dict:
    if rule is None:
        return {}

    return {
        "minimum_cgpa": _serialize_decimal(rule.minimum_cgpa),
        "allowed_departments": rule.allowed_departments,
        "allowed_graduation_years": rule.allowed_graduation_years,
        "maximum_active_backlogs": rule.maximum_active_backlogs,
        "allow_backlog_history": rule.allow_backlog_history,
        "gender_restriction": rule.gender_restriction,
        "education_requirements": rule.education_requirements,
    }
