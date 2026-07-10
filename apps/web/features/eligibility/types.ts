export type EligibilityReasonCode =
  | "PROFILE_MISSING"
  | "ACADEMIC_INFO_MISSING"
  | "PERSONAL_INFO_MISSING"
  | "CGPA_BELOW_MINIMUM"
  | "DEPARTMENT_NOT_ALLOWED"
  | "GRADUATION_YEAR_NOT_ALLOWED"
  | "ACTIVE_BACKLOGS_EXCEEDED"
  | "BACKLOG_HISTORY_NOT_ALLOWED"
  | "GENDER_RESTRICTED"
  | "EDUCATION_TYPE_MISSING"
  | "EDUCATION_SCORE_BELOW_MINIMUM";

export type EligibilityReason = {
  code: EligibilityReasonCode;
  title: string;
  expected: string;
  actual: string;
};

export type EligibilityEvaluation = {
  eligible: boolean;
  student_profile_id: string;
  hiring_opportunity_id: string;
  reasons: EligibilityReason[];
};

export type ReasonBreakdownItem = {
  code: EligibilityReasonCode;
  title: string;
  count: number;
};

export type ScreeningSummary = {
  hiring_opportunity_id: string;
  total_applications: number;
  eligible_count: number;
  ineligible_count: number;
  reason_breakdown: ReasonBreakdownItem[];
};
