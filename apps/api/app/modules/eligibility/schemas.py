import uuid

from pydantic import BaseModel, ConfigDict, Field

from app.modules.eligibility.enums import EligibilityReasonCode


class EligibilityReason(BaseModel):
    code: EligibilityReasonCode
    title: str
    expected: str
    actual: str


class EligibilityEvaluationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    eligible: bool
    student_profile_id: uuid.UUID
    hiring_opportunity_id: uuid.UUID
    reasons: list[EligibilityReason] = Field(default_factory=list)


class ReasonBreakdownItem(BaseModel):
    code: EligibilityReasonCode
    title: str
    count: int


class ScreeningSummaryResponse(BaseModel):
    hiring_opportunity_id: uuid.UUID
    total_applications: int
    eligible_count: int
    ineligible_count: int
    reason_breakdown: list[ReasonBreakdownItem] = Field(default_factory=list)
