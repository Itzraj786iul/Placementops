import type {
  ApplicationListItem,
  ApplicationStatus,
  EligibilityRule,
  OpportunityDetail,
  TimelineStage,
} from "@/features/student-opportunities/types";

export type { EligibilityRule };

export type OperationsTab =
  "overview" | "applications" | "screening" | "documents" | "timeline";

export type TimelineEntry = {
  id: string;
  hiring_opportunity_id: string;
  stage: TimelineStage;
  created_by: string;
  created_at: string;
  remarks: string | null;
};

export type ApplicationAnswer = {
  id: string;
  application_question_id: string;
  answer: string;
};

export type ApplicationDetail = ApplicationListItem & {
  submitted_by: string;
  answers: ApplicationAnswer[];
};

export type ProfileSnapshot = {
  id: string;
  roll_number: string;
  department_name: string | null;
  department_code: string | null;
  graduation_year: number;
  personal_information: {
    first_name: string;
    last_name: string;
    gender: string;
    personal_email: string | null;
  } | null;
  academic_information: {
    current_cgpa: string | null;
    active_backlogs: number;
  } | null;
};

export type ResumeSnapshot = {
  id: string;
  name: string;
  file_url: string;
  version: number;
};

export type ApplicationSnapshot = {
  application_id: string;
  student_profile_snapshot: ProfileSnapshot;
  resume_snapshot: ResumeSnapshot;
  eligibility_snapshot: Record<string, unknown>;
};

export type EnrichedApplication = {
  application: ApplicationListItem;
  snapshot?: ApplicationSnapshot;
  detail?: ApplicationDetail;
};

export type ApplicationFilters = {
  search: string;
  status: ApplicationStatus | null;
  department: string | null;
  branch: string | null;
};

export type ApplicationSortField =
  "name" | "roll_number" | "department" | "cgpa" | "applied_at" | "status";

export type SortDirection = "asc" | "desc";

export type OpportunityWithCompany = OpportunityDetail & {
  companyName: string;
};
