from app.modules.students.enums import DocumentType
from app.modules.students.models import StudentProfile
from app.modules.students.schemas import PROFILE_COMPLETION_WEIGHTS

REQUIRED_DOCUMENT_TYPES = {
    DocumentType.PHOTO,
    DocumentType.AADHAR,
    DocumentType.TENTH_MARKSHEET,
    DocumentType.TWELFTH_MARKSHEET,
}


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
