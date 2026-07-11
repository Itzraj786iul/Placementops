import uuid

from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from app.modules.students.dependencies import get_student_service
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
    PersonalInformationCreate,
    PersonalInformationResponse,
    PersonalInformationUpdate,
    ProfilePhotoUploadResponse,
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
from app.modules.students.service import StudentService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user
from app.platform.storage.types import UploadCategory
from app.platform.storage.upload_io import read_upload_capped

students_router = APIRouter(prefix="/students", tags=["students"])


@students_router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(
    _: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> list[DepartmentResponse]:
    return service.list_departments()


@students_router.post(
    "/profiles",
    response_model=StudentProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    payload: StudentProfileCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    return service.create_profile(current_user, payload)


@students_router.get("/profiles/me", response_model=StudentProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    return service.get_my_profile(current_user)


@students_router.post(
    "/profiles/me/submit",
    response_model=StudentProfileResponse,
)
def submit_my_profile(
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    """Student-only: submit own profile for placement review."""
    return service.submit_my_profile(current_user)


@students_router.get("/profiles/{profile_id}", response_model=StudentProfileResponse)
def get_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    return service.get_profile(current_user, profile_id)


@students_router.patch("/profiles/{profile_id}", response_model=StudentProfileResponse)
def update_profile(
    profile_id: uuid.UUID,
    payload: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> StudentProfileResponse:
    return service.update_profile(current_user, profile_id, payload)


@students_router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_profile(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> Response:
    service.delete_profile(current_user, profile_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@students_router.put(
    "/profiles/{profile_id}/personal-information",
    response_model=PersonalInformationResponse,
)
def upsert_personal_information(
    profile_id: uuid.UUID,
    payload: PersonalInformationCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> PersonalInformationResponse:
    return service.upsert_personal_information(current_user, profile_id, payload)


@students_router.get(
    "/profiles/{profile_id}/personal-information",
    response_model=PersonalInformationResponse,
)
def get_personal_information(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> PersonalInformationResponse:
    return service.get_personal_information(current_user, profile_id)


@students_router.post(
    "/profiles/{profile_id}/personal-information/photo",
    response_model=ProfilePhotoUploadResponse,
)
async def upload_profile_photo(
    profile_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> ProfilePhotoUploadResponse:
    filename, content, content_type = await read_upload_capped(
        file,
        UploadCategory.IMAGE,
    )
    result = service.upload_profile_photo(
        current_user,
        profile_id,
        filename=filename,
        content=content,
        content_type=content_type,
    )
    return ProfilePhotoUploadResponse(photo_url=result["photo_url"])


@students_router.put(
    "/profiles/{profile_id}/academic-information",
    response_model=AcademicInformationResponse,
)
def upsert_academic_information(
    profile_id: uuid.UUID,
    payload: AcademicInformationCreate,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> AcademicInformationResponse:
    return service.upsert_academic_information(current_user, profile_id, payload)


@students_router.get(
    "/profiles/{profile_id}/academic-information",
    response_model=AcademicInformationResponse,
)
def get_academic_information(
    profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: StudentService = Depends(get_student_service),
) -> AcademicInformationResponse:
    return service.get_academic_information(current_user, profile_id)
