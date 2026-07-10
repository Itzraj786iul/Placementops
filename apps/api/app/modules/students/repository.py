import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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
    StudentVerification,
)


class StudentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_department_by_id(self, department_id: uuid.UUID) -> Department | None:
        return self.db.get(Department, department_id)

    def list_departments(self) -> list[Department]:
        return list(self.db.scalars(select(Department).order_by(Department.name)).all())

    def get_profile_by_id(self, profile_id: uuid.UUID) -> StudentProfile | None:
        stmt = (
            select(StudentProfile)
            .options(
                selectinload(StudentProfile.department),
                selectinload(StudentProfile.personal_information),
                selectinload(StudentProfile.academic_information),
                selectinload(StudentProfile.education_history),
                selectinload(StudentProfile.resumes),
                selectinload(StudentProfile.documents),
                selectinload(StudentProfile.skills),
                selectinload(StudentProfile.projects),
                selectinload(StudentProfile.verification),
            )
            .where(StudentProfile.id == profile_id)
        )
        return self.db.scalars(stmt).first()

    def get_profile_by_user_id(self, user_id: uuid.UUID) -> StudentProfile | None:
        stmt = (
            select(StudentProfile)
            .options(selectinload(StudentProfile.department))
            .where(StudentProfile.user_id == user_id)
        )
        return self.db.scalars(stmt).first()

    def profile_exists_for_user(self, user_id: uuid.UUID) -> bool:
        stmt = select(StudentProfile.id).where(StudentProfile.user_id == user_id)
        return self.db.scalars(stmt).first() is not None

    def roll_number_exists(self, roll_number: str) -> bool:
        stmt = select(StudentProfile.id).where(StudentProfile.roll_number == roll_number)
        return self.db.scalars(stmt).first() is not None

    def registration_number_exists(self, registration_number: str) -> bool:
        stmt = select(StudentProfile.id).where(
            StudentProfile.registration_number == registration_number,
        )
        return self.db.scalars(stmt).first() is not None

    def create_profile(self, profile: StudentProfile) -> StudentProfile:
        self.db.add(profile)
        self.db.flush()
        return profile

    def delete_profile(self, profile: StudentProfile) -> None:
        self.db.delete(profile)

    def get_personal_info(
        self,
        profile_id: uuid.UUID,
    ) -> StudentPersonalInformation | None:
        return self.db.get(StudentPersonalInformation, profile_id)

    def save_personal_info(
        self,
        personal: StudentPersonalInformation,
    ) -> StudentPersonalInformation:
        self.db.add(personal)
        self.db.flush()
        return personal

    def get_academic_info(
        self,
        profile_id: uuid.UUID,
    ) -> StudentAcademicInformation | None:
        return self.db.get(StudentAcademicInformation, profile_id)

    def save_academic_info(
        self,
        academic: StudentAcademicInformation,
    ) -> StudentAcademicInformation:
        self.db.add(academic)
        self.db.flush()
        return academic

    def get_education_by_id(self, record_id: uuid.UUID) -> StudentEducationHistory | None:
        return self.db.get(StudentEducationHistory, record_id)

    def list_education(self, profile_id: uuid.UUID) -> list[StudentEducationHistory]:
        stmt = select(StudentEducationHistory).where(
            StudentEducationHistory.student_profile_id == profile_id,
        )
        return list(self.db.scalars(stmt).all())

    def save_education(self, record: StudentEducationHistory) -> StudentEducationHistory:
        self.db.add(record)
        self.db.flush()
        return record

    def delete_education(self, record: StudentEducationHistory) -> None:
        self.db.delete(record)

    def get_resume_by_id(self, resume_id: uuid.UUID) -> StudentResumeLibrary | None:
        return self.db.get(StudentResumeLibrary, resume_id)

    def list_resumes(self, profile_id: uuid.UUID) -> list[StudentResumeLibrary]:
        stmt = select(StudentResumeLibrary).where(
            StudentResumeLibrary.student_profile_id == profile_id,
        )
        return list(self.db.scalars(stmt).all())

    def save_resume(self, resume: StudentResumeLibrary) -> StudentResumeLibrary:
        self.db.add(resume)
        self.db.flush()
        return resume

    def delete_resume(self, resume: StudentResumeLibrary) -> None:
        self.db.delete(resume)

    def deactivate_resumes(self, profile_id: uuid.UUID) -> None:
        for resume in self.list_resumes(profile_id):
            resume.is_active = False

    def get_document_by_id(self, document_id: uuid.UUID) -> StudentDocument | None:
        return self.db.get(StudentDocument, document_id)

    def list_documents(self, profile_id: uuid.UUID) -> list[StudentDocument]:
        stmt = select(StudentDocument).where(
            StudentDocument.student_profile_id == profile_id,
        )
        return list(self.db.scalars(stmt).all())

    def save_document(self, document: StudentDocument) -> StudentDocument:
        self.db.add(document)
        self.db.flush()
        return document

    def delete_document(self, document: StudentDocument) -> None:
        self.db.delete(document)

    def get_skill_by_id(self, skill_id: uuid.UUID) -> StudentSkill | None:
        return self.db.get(StudentSkill, skill_id)

    def list_skills(self, profile_id: uuid.UUID) -> list[StudentSkill]:
        stmt = select(StudentSkill).where(StudentSkill.student_profile_id == profile_id)
        return list(self.db.scalars(stmt).all())

    def save_skill(self, skill: StudentSkill) -> StudentSkill:
        self.db.add(skill)
        self.db.flush()
        return skill

    def delete_skill(self, skill: StudentSkill) -> None:
        self.db.delete(skill)

    def get_project_by_id(self, project_id: uuid.UUID) -> StudentProject | None:
        return self.db.get(StudentProject, project_id)

    def list_projects(self, profile_id: uuid.UUID) -> list[StudentProject]:
        stmt = select(StudentProject).where(
            StudentProject.student_profile_id == profile_id,
        )
        return list(self.db.scalars(stmt).all())

    def save_project(self, project: StudentProject) -> StudentProject:
        self.db.add(project)
        self.db.flush()
        return project

    def delete_project(self, project: StudentProject) -> None:
        self.db.delete(project)

    def get_verification(self, profile_id: uuid.UUID) -> StudentVerification | None:
        return self.db.get(StudentVerification, profile_id)

    def save_verification(
        self,
        verification: StudentVerification,
    ) -> StudentVerification:
        self.db.add(verification)
        self.db.flush()
        return verification
