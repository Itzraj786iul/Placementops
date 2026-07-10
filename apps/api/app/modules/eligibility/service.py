from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.modules.eligibility.access import (
    ensure_opportunity_read_access,
    ensure_staff_access,
    ensure_student_evaluation_access,
)
from app.modules.eligibility.evaluator import evaluate_student, is_eligible
from app.modules.eligibility.repository import EligibilityRepository
from app.modules.eligibility.schemas import (
    EligibilityEvaluationResponse,
    ScreeningSummaryResponse,
)
from app.modules.eligibility.screening import aggregate_screening
from app.modules.users.models import User


class EligibilityService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repository = EligibilityRepository(db)

    def evaluate_student(
        self,
        user: User,
        opportunity_id: uuid.UUID,
        student_profile_id: uuid.UUID,
    ) -> EligibilityEvaluationResponse:
        opportunity = self.repository.get_opportunity(opportunity_id)
        ensure_opportunity_read_access(user, opportunity)

        profile = self.repository.get_profile(student_profile_id)
        ensure_student_evaluation_access(user, profile)

        rule = opportunity.eligibility_rule if opportunity else None
        reasons = evaluate_student(rule, profile)

        return EligibilityEvaluationResponse(
            eligible=is_eligible(reasons),
            student_profile_id=student_profile_id,
            hiring_opportunity_id=opportunity_id,
            reasons=reasons,
        )

    def get_screening_summary(
        self,
        user: User,
        opportunity_id: uuid.UUID,
    ) -> ScreeningSummaryResponse:
        ensure_staff_access(user)

        opportunity = self.repository.get_opportunity(opportunity_id)
        ensure_opportunity_read_access(user, opportunity)

        profile_ids = self.repository.list_application_profile_ids(opportunity_id)
        profiles = self.repository.get_profiles_by_ids(profile_ids)
        profile_map = {profile.id: profile for profile in profiles}

        rule = opportunity.eligibility_rule if opportunity else None
        evaluations = [
            evaluate_student(rule, profile_map.get(profile_id))
            for profile_id in profile_ids
        ]
        return aggregate_screening(opportunity_id, evaluations)
