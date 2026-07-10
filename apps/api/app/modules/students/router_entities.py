import uuid

from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status

from app.modules.students.dependencies import get_student_service
from app.modules.students.enums import DocumentType
from app.modules.students.schemas import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    EducationHistoryCreate,
    EducationHistoryResponse,
    EducationHistoryUpdate,
    ProjectCreate,
    ProjectResponse,
    ProjectUpdate,
    ResumeCreate,
    ResumeResponse,
    ResumeUpdate,
    SkillCreate,
    SkillResponse,
    SkillUpdate,
    VerificationResponse,
    VerificationUpdate,
)
from app.modules.students.service import StudentService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user
from app.platform.storage.types import UploadCategory
from app.platform.storage.upload_io import read_upload_capped

entity_router = APIRouter(prefix="/profiles/{profile_id}", tags=["students"])


@entity_router.post(
    "/education-history",
    response_model=EducationHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_education(
    profile_id: uuid.UUID,
    payload: EducationHistoryCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> EducationHistoryResponse:
    return service.create_education(current_user, profile_id, payload)


@entity_router.get("/education-history", response_model=list[EducationHistoryResponse])
def list_education(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> list[EducationHistoryResponse]:
    return service.list_education(current_user, profile_id)


@entity_router.patch(
    "/education-history/{record_id}",
    response_model=EducationHistoryResponse,
)
def update_education(
    profile_id: uuid.UUID,
    record_id: uuid.UUID,
    payload: EducationHistoryUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> EducationHistoryResponse:
    return service.update_education(current_user, profile_id, record_id, payload)


@entity_router.delete(
    "/education-history/{record_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_education(
    profile_id: uuid.UUID,
    record_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> Response:
    service.delete_education(current_user, profile_id, record_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@entity_router.post(
    "/resumes",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_resume(
    profile_id: uuid.UUID,
    payload: ResumeCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ResumeResponse:
    return service.create_resume(current_user, profile_id, payload)


@entity_router.post(
    "/resumes/upload",
    response_model=ResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_resume(
    profile_id: uuid.UUID,
    file: UploadFile = File(...),
    name: str | None = Form(default=None),
    is_active: bool = Form(default=False),
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ResumeResponse:
    filename, content, content_type = await read_upload_capped(
        file,
        UploadCategory.RESUME,
    )
    return service.upload_resume(
        current_user,
        profile_id,
        filename=filename,
        content=content,
        content_type=content_type,
        name=name,
        is_active=is_active,
    )


@entity_router.post(
    "/resumes/{resume_id}/replace",
    response_model=ResumeResponse,
)
async def replace_resume(
    profile_id: uuid.UUID,
    resume_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ResumeResponse:
    filename, content, content_type = await read_upload_capped(
        file,
        UploadCategory.RESUME,
    )
    return service.replace_resume_file(
        current_user,
        profile_id,
        resume_id,
        filename=filename,
        content=content,
        content_type=content_type,
    )


@entity_router.get("/resumes", response_model=list[ResumeResponse])
def list_resumes(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> list[ResumeResponse]:
    return service.list_resumes(current_user, profile_id)


@entity_router.patch("/resumes/{resume_id}", response_model=ResumeResponse)
def update_resume(
    profile_id: uuid.UUID,
    resume_id: uuid.UUID,
    payload: ResumeUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ResumeResponse:
    return service.update_resume(current_user, profile_id, resume_id, payload)


@entity_router.delete("/resumes/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    profile_id: uuid.UUID,
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> Response:
    service.delete_resume(current_user, profile_id, resume_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@entity_router.post(
    "/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    profile_id: uuid.UUID,
    payload: DocumentCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> DocumentResponse:
    return service.create_document(current_user, profile_id, payload)


@entity_router.post(
    "/documents/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    profile_id: uuid.UUID,
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    file_name: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> DocumentResponse:
    category = (
        UploadCategory.IMAGE
        if document_type == DocumentType.PHOTO
        else UploadCategory.DOCUMENT
    )
    filename, content, content_type = await read_upload_capped(file, category)
    return service.upload_document(
        current_user,
        profile_id,
        filename=filename,
        content=content,
        content_type=content_type,
        document_type=document_type,
        file_name=file_name,
    )


@entity_router.post(
    "/documents/{document_id}/replace",
    response_model=DocumentResponse,
)
async def replace_document(
    profile_id: uuid.UUID,
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    file_name: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> DocumentResponse:
    # Cap at document max; service re-validates IMAGE vs DOCUMENT by type.
    filename, content, content_type = await read_upload_capped(
        file,
        UploadCategory.DOCUMENT,
    )
    return service.replace_document_file(
        current_user,
        profile_id,
        document_id,
        filename=filename,
        content=content,
        content_type=content_type,
        file_name=file_name,
    )


@entity_router.get("/documents", response_model=list[DocumentResponse])
def list_documents(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> list[DocumentResponse]:
    return service.list_documents(current_user, profile_id)


@entity_router.patch("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    profile_id: uuid.UUID,
    document_id: uuid.UUID,
    payload: DocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> DocumentResponse:
    return service.update_document(current_user, profile_id, document_id, payload)


@entity_router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    profile_id: uuid.UUID,
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> Response:
    service.delete_document(current_user, profile_id, document_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@entity_router.post(
    "/skills",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_skill(
    profile_id: uuid.UUID,
    payload: SkillCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> SkillResponse:
    return service.create_skill(current_user, profile_id, payload)


@entity_router.get("/skills", response_model=list[SkillResponse])
def list_skills(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> list[SkillResponse]:
    return service.list_skills(current_user, profile_id)


@entity_router.patch("/skills/{skill_id}", response_model=SkillResponse)
def update_skill(
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    payload: SkillUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> SkillResponse:
    return service.update_skill(current_user, profile_id, skill_id, payload)


@entity_router.delete("/skills/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    profile_id: uuid.UUID,
    skill_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> Response:
    service.delete_skill(current_user, profile_id, skill_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@entity_router.post(
    "/projects",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    profile_id: uuid.UUID,
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ProjectResponse:
    return service.create_project(current_user, profile_id, payload)


@entity_router.get("/projects", response_model=list[ProjectResponse])
def list_projects(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> list[ProjectResponse]:
    return service.list_projects(current_user, profile_id)


@entity_router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project(
    profile_id: uuid.UUID,
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ProjectResponse:
    return service.update_project(current_user, profile_id, project_id, payload)


@entity_router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    profile_id: uuid.UUID,
    project_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> Response:
    service.delete_project(current_user, profile_id, project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@entity_router.get("/verification", response_model=VerificationResponse)
def get_verification(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> VerificationResponse:
    return service.get_verification(current_user, profile_id)


@entity_router.patch("/verification", response_model=VerificationResponse)
def update_verification(
    profile_id: uuid.UUID,
    payload: VerificationUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> VerificationResponse:
    return service.update_verification(current_user, profile_id, payload)
