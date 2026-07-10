import type {
  EligibilityEvaluation,
  ScreeningSummary,
} from "@/features/eligibility/types";
import { apiRequest } from "@/lib/api-client";

export async function fetchScreeningSummary(
  opportunityId: string,
): Promise<ScreeningSummary> {
  return apiRequest<ScreeningSummary>(
    `/opportunities/${opportunityId}/screening`,
  );
}

export async function evaluateStudentEligibility(
  opportunityId: string,
  studentProfileId: string,
): Promise<EligibilityEvaluation> {
  return apiRequest<EligibilityEvaluation>(
    `/opportunities/${opportunityId}/screening/student/${studentProfileId}`,
    { method: "POST" },
  );
}
