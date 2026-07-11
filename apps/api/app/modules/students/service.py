import uuid
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.students.access import ensure_profile_access, ensure_staff_access, is_staff_user
from app.modules.students.completion import calculate_profile_completion
from app.modules.students.enums import ProfileStatus
from app.modules.students.enums import DocumentType
from app.modules.students.exceptions import (
    StudentConflictError,
    StudentNotFoundError,
    StudentValidationError,
)
from app.modules.students.models import (
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
from app.modules.students.repository import StudentRepository
from app.modules.students.schemas import (
    AcademicInformationCreate,
    AcademicInformationResponse,
    AcademicInformationUpdate,
    DepartmentResponse,
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    EducationHistoryCreate,
    EducationHistoryResponse,
    EducationHistoryUpdate,
    PROFILE_COMPLETION_WEIGHTS,
    PersonalInformationCreate,
    PersonalInformationResponse,
    PersonalInformationUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ResumeCreate,
    ResumeResponse,
    ResumeUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    StudentProfileCreate,
    StudentProfileResponse,
    StudentProfileUpdate,
    VerificationResponse,
    VerificationUpdate,
)
from app.modules.audit.enums import AuditAction, AuditEntityType
from app.modules.audit.recorder import record_audit
from app.modules.audit.serialize import snapshot_fields
from app.modules.users.models import User
from app.platform.permissions.permissions import has_role
from app.platform.storage.cloudinary_service import CloudinaryService
from app.platform.storage.dependencies import get_cloudinary_service
from app.platform.storage.types import UploadCategory
from app.utils.datetime import utc_now

_PROFILE_AUDIT_FIELDS = [
    "roll_number",
    "registration_number",
    "department_id",
    "graduation_year",
    "profile_status",
    "profile_completion",
]


class StudentService:
    def __init__(self, db: Session, storage: CloudinaryService | None = None) -> None:
        self.db = db
        self.repository = StudentRepository(db)
        self.storage = storage or get_cloudinary_service()

    def list_departments(self) -> list[DepartmentResponse]:
        return [
            DepartmentResponse.model_validate(department)
            for department in self.repository.list_departments()
        ]

    def create_profile(
        self,
        user: User,
        payload: StudentProfileCreate,
    ) -> StudentProfileResponse:
        if not has_role(user, "STUDENT") and not is_staff_user(user):
            raise StudentValidationError("Only students can create a student profile")

        if self.repository.profile_exists_for_user(user.id):
            raise StudentConflictError("A student profile already exists for this user")

        if self.repository.roll_number_exists(payload.roll_number):
            raise StudentConflictError("Roll number is already registered")

        if self.repository.registration_number_exists(payload.registration_number):
            raise StudentConflictError("Registration number is already registered")

        department = self.repository.get_department_by_id(payload.department_id)
        if department is None:
            raise StudentValidationError("Selected department does not exist")
        if getattr(department, "status", "active") == "archived":
            raise StudentValidationError(
                "Archived departments cannot receive new students",
            )

        profile = StudentProfile(
            user_id=user.id,
            department_id=payload.department_id,
            roll_number=payload.roll_number,
            registration_number=payload.registration_number,
            graduation_year=payload.graduation_year,
            profile_status=ProfileStatus.DRAFT,
            profile_completion=PROFILE_COMPLETION_WEIGHTS["core"],
        )
        self.repository.create_profile(profile)
        verification = StudentVerification(student_profile_id=profile.id)
        self.repository.save_verification(verification)
        record_audit(
            self.db,
            entity_type=AuditEntityType.STUDENT_PROFILE,
            entity_id=profile.id,
            action=AuditAction.CREATE,
            performed_by=user.id,
            new_values=snapshot_fields(profile, _PROFILE_AUDIT_FIELDS),
        )
        self.db.commit()
        return self._profile_response(self.repository.get_profile_by_id(profile.id))

    def get_my_profile(self, user: User) -> StudentProfileResponse:
        profile = self.repository.get_profile_by_user_id(user.id)
        profile = ensure_profile_access(user, profile)
        return self._profile_response(profile)

    def get_profile(self, user: User, profile_id: uuid.UUID) -> StudentProfileResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        return self._profile_response(profile)

    def update_profile(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: StudentProfileUpdate,
    ) -> StudentProfileResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        old_values = snapshot_fields(profile, _PROFILE_AUDIT_FIELDS)
        previous_status = profile.profile_status

        if payload.roll_number and payload.roll_number != profile.roll_number:
            if self.repository.roll_number_exists(payload.roll_number):
                raise StudentConflictError("Roll number is already registered")
            profile.roll_number = payload.roll_number

        if (
            payload.registration_number
            and payload.registration_number != profile.registration_number
        ):
            if self.repository.registration_number_exists(payload.registration_number):
                raise StudentConflictError("Registration number is already registered")
            profile.registration_number = payload.registration_number

        if payload.department_id is not None:
            department = self.repository.get_department_by_id(payload.department_id)
            if department is None:
                raise StudentValidationError("Selected department does not exist")
            if getattr(department, "status", "active") == "archived":
                raise StudentValidationError(
                    "Archived departments cannot receive new students",
                )
            profile.department_id = payload.department_id

        if payload.graduation_year is not None:
            profile.graduation_year = payload.graduation_year

        if payload.profile_status is not None:
            if not is_staff_user(user):
                raise StudentValidationError("Only staff can update profile status")
            profile.profile_status = payload.profile_status

        profile.updated_at = utc_now()
        self._refresh_completion(profile)
        record_audit(
            self.db,
            entity_type=AuditEntityType.STUDENT_PROFILE,
            entity_id=profile.id,
            action=AuditAction.UPDATE,
            performed_by=user.id,
            old_values=old_values,
            new_values=snapshot_fields(profile, _PROFILE_AUDIT_FIELDS),
            metadata=(
                {"submitted": True}
                if (
                    previous_status != ProfileStatus.SUBMITTED
                    and profile.profile_status == ProfileStatus.SUBMITTED
                )
                else None
            ),
        )
        self.db.commit()
        return self._profile_response(self.repository.get_profile_by_id(profile.id))

    def delete_profile(self, user: User, profile_id: uuid.UUID) -> None:
        ensure_staff_access(user)
        profile = self.repository.get_profile_by_id(profile_id)
        if profile is None:
            raise StudentNotFoundError()
        old_values = snapshot_fields(profile, _PROFILE_AUDIT_FIELDS)
        record_audit(
            self.db,
            entity_type=AuditEntityType.STUDENT_PROFILE,
            entity_id=profile.id,
            action=AuditAction.DELETE,
            performed_by=user.id,
            old_values=old_values,
        )
        self.repository.delete_profile(profile)
        self.db.commit()

    def upsert_personal_information(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: PersonalInformationCreate | PersonalInformationUpdate,
    ) -> PersonalInformationResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        existing = self.repository.get_personal_info(profile_id)
        if existing is None:
            personal = StudentPersonalInformation(
                student_profile_id=profile_id,
                **payload.model_dump(),
            )
        else:
            for field, value in payload.model_dump().items():
                setattr(existing, field, value)
            personal = existing
        self.repository.save_personal_info(personal)
        self._refresh_completion(profile)
        self.db.commit()
        return PersonalInformationResponse.model_validate(personal)

    def get_personal_information(
        self,
        user: User,
        profile_id: uuid.UUID,
    ) -> PersonalInformationResponse:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        personal = self.repository.get_personal_info(profile_id)
        if personal is None:
            raise StudentNotFoundError("Personal information not found")
        return PersonalInformationResponse.model_validate(personal)

    def upsert_academic_information(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: AcademicInformationCreate | AcademicInformationUpdate,
    ) -> AcademicInformationResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        existing = self.repository.get_academic_info(profile_id)
        if existing is None:
            academic = StudentAcademicInformation(
                student_profile_id=profile_id,
                **payload.model_dump(),
            )
        else:
            for field, value in payload.model_dump().items():
                setattr(existing, field, value)
            academic = existing
        self.repository.save_academic_info(academic)
        self._refresh_completion(profile)
        self.db.commit()
        return AcademicInformationResponse.model_validate(academic)

    def get_academic_information(
        self,
        user: User,
        profile_id: uuid.UUID,
    ) -> AcademicInformationResponse:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        academic = self.repository.get_academic_info(profile_id)
        if academic is None:
            raise StudentNotFoundError("Academic information not found")
        return AcademicInformationResponse.model_validate(academic)

    def create_education(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: EducationHistoryCreate,
    ) -> EducationHistoryResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        record = StudentEducationHistory(
            student_profile_id=profile_id,
            **payload.model_dump(),
        )
        self.repository.save_education(record)
        self._refresh_completion(profile)
        self.db.commit()
        return EducationHistoryResponse.model_validate(record)

    def list_education(
        self,
        user: User,
        profile_id: uuid.UUID,
    ) -> list[EducationHistoryResponse]:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        return [
            EducationHistoryResponse.model_validate(record)
            for record in self.repository.list_education(profile_id)
        ]

    def update_education(
        self,
        user: User,
        profile_id: uuid.UUID,
        record_id: uuid.UUID,
        payload: EducationHistoryUpdate,
    ) -> EducationHistoryResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        record = self.repository.get_education_by_id(record_id)
        if record is None or record.student_profile_id != profile_id:
            raise StudentNotFoundError("Education record not found")
        for field, value in payload.model_dump().items():
            setattr(record, field, value)
        self._refresh_completion(profile)
        self.db.commit()
        return EducationHistoryResponse.model_validate(record)

    def delete_education(
        self,
        user: User,
        profile_id: uuid.UUID,
        record_id: uuid.UUID,
    ) -> None:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        record = self.repository.get_education_by_id(record_id)
        if record is None or record.student_profile_id != profile_id:
            raise StudentNotFoundError("Education record not found")
        self.repository.delete_education(record)
        self._refresh_completion(profile)
        self.db.commit()

    def create_resume(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: ResumeCreate,
    ) -> ResumeResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        if payload.is_active:
            self.repository.deactivate_resumes(profile_id)
        resume = StudentResumeLibrary(
            student_profile_id=profile_id,
            **payload.model_dump(),
        )
        self.repository.save_resume(resume)
        self._refresh_completion(profile)
        self.db.commit()
        return ResumeResponse.model_validate(resume)

    def upload_resume(
        self,
        user: User,
        profile_id: uuid.UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        name: str | None = None,
        is_active: bool = False,
    ) -> ResumeResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        stored = self.storage.upload(
            filename=filename,
            content=content,
            content_type=content_type,
            category=UploadCategory.RESUME,
            folder=f"placementos/students/{profile_id}/resumes",
        )
        if is_active:
            self.repository.deactivate_resumes(profile_id)
        resume = StudentResumeLibrary(
            student_profile_id=profile_id,
            name=(name or stored.original_filename)[:150],
            file_url=stored.url[:500],
            version=1,
            is_active=is_active,
        )
        self.repository.save_resume(resume)
        self._refresh_completion(profile)
        self.db.commit()
        return ResumeResponse.model_validate(resume)

    def replace_resume_file(
        self,
        user: User,
        profile_id: uuid.UUID,
        resume_id: uuid.UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
    ) -> ResumeResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        resume = self.repository.get_resume_by_id(resume_id)
        if resume is None or resume.student_profile_id != profile_id:
            raise StudentNotFoundError("Resume not found")
        stored = self.storage.replace(
            filename=filename,
            content=content,
            content_type=content_type,
            category=UploadCategory.RESUME,
            folder=f"placementos/students/{profile_id}/resumes",
            old_url=resume.file_url,
        )
        resume.file_url = stored.url[:500]
        resume.version = (resume.version or 1) + 1
        self._refresh_completion(profile)
        self.db.commit()
        return ResumeResponse.model_validate(resume)

    def list_resumes(self, user: User, profile_id: uuid.UUID) -> list[ResumeResponse]:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        return [
            ResumeResponse.model_validate(resume)
            for resume in self.repository.list_resumes(profile_id)
        ]

    def update_resume(
        self,
        user: User,
        profile_id: uuid.UUID,
        resume_id: uuid.UUID,
        payload: ResumeUpdate,
    ) -> ResumeResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        resume = self.repository.get_resume_by_id(resume_id)
        if resume is None or resume.student_profile_id != profile_id:
            raise StudentNotFoundError("Resume not found")
        if payload.is_active:
            self.repository.deactivate_resumes(profile_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(resume, field, value)
        self._refresh_completion(profile)
        self.db.commit()
        return ResumeResponse.model_validate(resume)

    def delete_resume(
        self,
        user: User,
        profile_id: uuid.UUID,
        resume_id: uuid.UUID,
    ) -> None:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        resume = self.repository.get_resume_by_id(resume_id)
        if resume is None or resume.student_profile_id != profile_id:
            raise StudentNotFoundError("Resume not found")
        file_url = resume.file_url
        self.repository.delete_resume(resume)
        self._refresh_completion(profile)
        self.db.commit()
        try:
            self.storage.delete(file_url)
        except Exception:  # noqa: BLE001 — DB delete already committed
            pass

    def create_document(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: DocumentCreate,
    ) -> DocumentResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        document = StudentDocument(student_profile_id=profile_id, **payload.model_dump())
        self.repository.save_document(document)
        self._refresh_completion(profile)
        self.db.commit()
        return DocumentResponse.model_validate(document)

    def upload_document(
        self,
        user: User,
        profile_id: uuid.UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        document_type: DocumentType,
        file_name: str | None = None,
    ) -> DocumentResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        category = (
            UploadCategory.IMAGE
            if document_type == DocumentType.PHOTO
            else UploadCategory.DOCUMENT
        )
        stored = self.storage.upload(
            filename=filename,
            content=content,
            content_type=content_type,
            category=category,
            folder=f"placementos/students/{profile_id}/documents",
        )
        existing = next(
            (
                doc
                for doc in self.repository.list_documents(profile_id)
                if doc.document_type == document_type
            ),
            None,
        )
        if existing is not None:
            old_url = existing.file_url
            existing.file_url = stored.url[:500]
            existing.file_name = (file_name or stored.original_filename)[:255]
            self._refresh_completion(profile)
            self.db.commit()
            try:
                self.storage.delete(old_url)
            except Exception:  # noqa: BLE001
                pass
            return DocumentResponse.model_validate(existing)

        document = StudentDocument(
            student_profile_id=profile_id,
            document_type=document_type,
            file_url=stored.url[:500],
            file_name=(file_name or stored.original_filename)[:255],
        )
        self.repository.save_document(document)
        self._refresh_completion(profile)
        self.db.commit()
        return DocumentResponse.model_validate(document)

    def replace_document_file(
        self,
        user: User,
        profile_id: uuid.UUID,
        document_id: uuid.UUID,
        *,
        filename: str,
        content: bytes,
        content_type: str | None,
        file_name: str | None = None,
    ) -> DocumentResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        document = self.repository.get_document_by_id(document_id)
        if document is None or document.student_profile_id != profile_id:
            raise StudentNotFoundError("Document not found")
        category = (
            UploadCategory.IMAGE
            if document.document_type == DocumentType.PHOTO
            else UploadCategory.DOCUMENT
        )
        stored = self.storage.replace(
            filename=filename,
            content=content,
            content_type=content_type,
            category=category,
            folder=f"placementos/students/{profile_id}/documents",
            old_url=document.file_url,
        )
        document.file_url = stored.url[:500]
        if file_name:
            document.file_name = file_name[:255]
        else:
            document.file_name = stored.original_filename[:255]
        self._refresh_completion(profile)
        self.db.commit()
        return DocumentResponse.model_validate(document)

    def list_documents(
        self,
        user: User,
        profile_id: uuid.UUID,
    ) -> list[DocumentResponse]:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        return [
            DocumentResponse.model_validate(document)
            for document in self.repository.list_documents(profile_id)
        ]

    def update_document(
        self,
        user: User,
        profile_id: uuid.UUID,
        document_id: uuid.UUID,
        payload: DocumentUpdate,
    ) -> DocumentResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        document = self.repository.get_document_by_id(document_id)
        if document is None or document.student_profile_id != profile_id:
            raise StudentNotFoundError("Document not found")
        if payload.status is not None and not is_staff_user(user):
            raise StudentValidationError("Only staff can update document status")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(document, field, value)
        self._refresh_completion(profile)
        self.db.commit()
        return DocumentResponse.model_validate(document)

    def delete_document(
        self,
        user: User,
        profile_id: uuid.UUID,
        document_id: uuid.UUID,
    ) -> None:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        document = self.repository.get_document_by_id(document_id)
        if document is None or document.student_profile_id != profile_id:
            raise StudentNotFoundError("Document not found")
        file_url = document.file_url
        self.repository.delete_document(document)
        self._refresh_completion(profile)
        self.db.commit()
        try:
            self.storage.delete(file_url)
        except Exception:  # noqa: BLE001
            pass

    def create_skill(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: SkillCreate,
    ) -> SkillResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        skill = StudentSkill(student_profile_id=profile_id, **payload.model_dump())
        self.repository.save_skill(skill)
        self._refresh_completion(profile)
        self.db.commit()
        return SkillResponse.model_validate(skill)

    def list_skills(self, user: User, profile_id: uuid.UUID) -> list[SkillResponse]:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        return [
            SkillResponse.model_validate(skill)
            for skill in self.repository.list_skills(profile_id)
        ]

    def update_skill(
        self,
        user: User,
        profile_id: uuid.UUID,
        skill_id: uuid.UUID,
        payload: SkillUpdate,
    ) -> SkillResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        skill = self.repository.get_skill_by_id(skill_id)
        if skill is None or skill.student_profile_id != profile_id:
            raise StudentNotFoundError("Skill not found")
        for field, value in payload.model_dump().items():
            setattr(skill, field, value)
        self._refresh_completion(profile)
        self.db.commit()
        return SkillResponse.model_validate(skill)

    def delete_skill(
        self,
        user: User,
        profile_id: uuid.UUID,
        skill_id: uuid.UUID,
    ) -> None:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        skill = self.repository.get_skill_by_id(skill_id)
        if skill is None or skill.student_profile_id != profile_id:
            raise StudentNotFoundError("Skill not found")
        self.repository.delete_skill(skill)
        self._refresh_completion(profile)
        self.db.commit()

    def create_project(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: ProjectCreate,
    ) -> ProjectResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        project = StudentProject(student_profile_id=profile_id, **payload.model_dump())
        self.repository.save_project(project)
        self._refresh_completion(profile)
        self.db.commit()
        return ProjectResponse.model_validate(project)

    def list_projects(self, user: User, profile_id: uuid.UUID) -> list[ProjectResponse]:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        return [
            ProjectResponse.model_validate(project)
            for project in self.repository.list_projects(profile_id)
        ]

    def update_project(
        self,
        user: User,
        profile_id: uuid.UUID,
        project_id: uuid.UUID,
        payload: ProjectUpdate,
    ) -> ProjectResponse:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        project = self.repository.get_project_by_id(project_id)
        if project is None or project.student_profile_id != profile_id:
            raise StudentNotFoundError("Project not found")
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(project, field, value)
        self._refresh_completion(profile)
        self.db.commit()
        return ProjectResponse.model_validate(project)

    def delete_project(
        self,
        user: User,
        profile_id: uuid.UUID,
        project_id: uuid.UUID,
    ) -> None:
        profile = ensure_profile_access(
            user,
            self.repository.get_profile_by_id(profile_id),
        )
        project = self.repository.get_project_by_id(project_id)
        if project is None or project.student_profile_id != profile_id:
            raise StudentNotFoundError("Project not found")
        self.repository.delete_project(project)
        self._refresh_completion(profile)
        self.db.commit()

    def get_verification(
        self,
        user: User,
        profile_id: uuid.UUID,
    ) -> VerificationResponse:
        ensure_profile_access(user, self.repository.get_profile_by_id(profile_id))
        verification = self.repository.get_verification(profile_id)
        if verification is None:
            raise StudentNotFoundError("Verification record not found")
        return VerificationResponse.model_validate(verification)

    def update_verification(
        self,
        user: User,
        profile_id: uuid.UUID,
        payload: VerificationUpdate,
    ) -> VerificationResponse:
        ensure_staff_access(user)
        profile = self.repository.get_profile_by_id(profile_id)
        if profile is None:
            raise StudentNotFoundError()
        verification = self.repository.get_verification(profile_id)
        if verification is None:
            raise StudentNotFoundError("Verification record not found")
        old_values = {
            key: getattr(verification, key)
            for key in payload.model_dump(exclude_unset=True)
        }
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(verification, field, value)
        if any(
            value is not None
            for key, value in payload.model_dump(exclude_unset=True).items()
            if key.endswith("_status")
        ):
            verification.reviewer_id = user.id
            verification.reviewed_at = utc_now()
        record_audit(
            self.db,
            entity_type=AuditEntityType.STUDENT_PROFILE,
            entity_id=profile.id,
            action=AuditAction.VERIFY,
            performed_by=user.id,
            old_values=old_values,
            new_values=payload.model_dump(exclude_unset=True),
        )
        self.db.commit()
        return VerificationResponse.model_validate(verification)

    def _refresh_completion(self, profile: StudentProfile) -> None:
        loaded = self.repository.get_profile_by_id(profile.id)
        if loaded is None:
            return
        loaded.profile_completion = calculate_profile_completion(loaded)
        loaded.updated_at = utc_now()

    def _profile_response(self, profile: StudentProfile | None) -> StudentProfileResponse:
        if profile is None:
            raise StudentNotFoundError()
        return StudentProfileResponse.model_validate(profile)
