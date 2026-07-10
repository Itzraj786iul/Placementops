import uuid

from fastapi import APIRouter, Depends

from app.modules.eligibility.dependencies import get_eligibility_service
from app.modules.eligibility.schemas import (
    EligibilityEvaluationResponse,
    ScreeningSummaryResponse,
)
from app.modules.eligibility.service import EligibilityService
from app.modules.users.models import User
from app.platform.auth.dependencies import get_current_user

eligibility_router = APIRouter(prefix="/opportunities", tags=["eligibility"])


@eligibility_router.get(
    "/{opportunity_id}/screening",
    response_model=ScreeningSummaryResponse,
)
def get_screening_summary(
    opportunity_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: EligibilityService = Depends(get_eligibility_service),
) -> ScreeningSummaryResponse:
    """Staff-only screening summary for an opportunity's applicants."""
    return service.get_screening_summary(current_user, opportunity_id)


@eligibility_router.post(
    "/{opportunity_id}/screening/student/{student_id}",
    response_model=EligibilityEvaluationResponse,
)
def evaluate_student_eligibility(
    opportunity_id: uuid.UUID,
    student_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    service: EligibilityService = Depends(get_eligibility_service),
) -> EligibilityEvaluationResponse:
    """
    Evaluate a single student profile against opportunity eligibility rules.

    Staff may evaluate any student. Students may evaluate only themselves.
    `student_id` is the student profile ID.
    """
    return service.evaluate_student(current_user, opportunity_id, student_id)
