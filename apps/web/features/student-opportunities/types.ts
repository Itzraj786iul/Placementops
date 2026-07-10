export type EmploymentType =
  "INTERNSHIP" | "FULL_TIME" | "PPO" | "INTERNSHIP_PPO";

export type WorkMode = "ONSITE" | "HYBRID" | "REMOTE";

export type OpportunityStatus = "DRAFT" | "PUBLISHED" | "ARCHIVED";

export type TimelineStage =
  | "DRAFT"
  | "PUBLISHED"
  | "APPLICATIONS_OPEN"
  | "APPLICATIONS_CLOSED"
  | "SHORTLIST_RELEASED"
  | "ASSESSMENT"
  | "INTERVIEW"
  | "SELECTED"
  | "OFFER_RELEASED"
  | "COMPLETED";

export type ApplicationStatus =
  | "APPLIED"
  | "UNDER_REVIEW"
  | "SHORTLISTED"
  | "ASSESSMENT"
  | "INTERVIEW"
  | "SELECTED"
  | "OFFER_RELEASED"
  | "ACCEPTED"
  | "REJECTED"
  | "WITHDRAWN";

export type QuestionType = "TEXT" | "BOOLEAN" | "NUMBER" | "CHOICE";

export type OpportunityTab =
  "overview" | "eligibility" | "documents" | "application";

export type OpportunityListItem = {
  id: string;
  company_id: string;
  title: string;
  role: string;
  employment_type: EmploymentType;
  location: string;
  mode: WorkMode;
  application_deadline: string;
  status: OpportunityStatus;
  created_at: string;
  current_timeline_stage: TimelineStage | null;
};

export type OpportunityDetail = OpportunityListItem & {
  ctc_min: string | null;
  ctc_max: string | null;
  bond_details: string | null;
  job_description: string;
  created_by: string;
  updated_at: string;
};

export type EligibilityRule = {
  id: string;
  hiring_opportunity_id: string;
  minimum_cgpa: string | null;
  allowed_departments: string[] | null;
  allowed_graduation_years: number[] | null;
  maximum_active_backlogs: number | null;
  allow_backlog_history: boolean;
  gender_restriction: string | null;
  education_requirements: Record<string, unknown> | null;
};

export type ApplicationListItem = {
  id: string;
  student_profile_id: string;
  hiring_opportunity_id: string;
  selected_resume_id: string;
  status: ApplicationStatus;
  applied_at: string;
  withdrawn_at: string | null;
};

export type ApplicationDetail = ApplicationListItem & {
  submitted_by: string;
  answers: { id: string; application_question_id: string; answer: string }[];
};

export type ApplyPayload = {
  selected_resume_id: string;
  answers: { application_question_id: string; answer: string }[];
};

export type OpportunityFilters = {
  search: string;
  employmentType: EmploymentType | null;
  location: string | null;
  mode: WorkMode | null;
  ctcMin: number | null;
  ctcMax: number | null;
  departmentId: string | null;
  applicationStatus: ApplicationStatus | "NOT_APPLIED" | null;
};

export type EnrichedOpportunity = {
  list: OpportunityListItem;
  detail?: OpportunityDetail;
  application?: ApplicationListItem;
  eligibility?: EligibilityRule;
};

export type EligibilityCheck = {
  eligible: boolean;
  reasons: string[];
};
