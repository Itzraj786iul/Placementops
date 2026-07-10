import type {
  ApplicationStatus,
  EmploymentType,
  WorkMode,
} from "@/features/student-opportunities/types";

export const EMPLOYMENT_TYPES: EmploymentType[] = [
  "INTERNSHIP",
  "FULL_TIME",
  "PPO",
  "INTERNSHIP_PPO",
];

export const WORK_MODES: WorkMode[] = ["ONSITE", "HYBRID", "REMOTE"];

export const EMPLOYMENT_LABELS: Record<EmploymentType, string> = {
  INTERNSHIP: "Internship",
  FULL_TIME: "Full Time",
  PPO: "PPO",
  INTERNSHIP_PPO: "Internship + PPO",
};

export const MODE_LABELS: Record<WorkMode, string> = {
  ONSITE: "Onsite",
  HYBRID: "Hybrid",
  REMOTE: "Remote",
};

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  APPLIED: "Applied",
  UNDER_REVIEW: "Under Review",
  SHORTLISTED: "Shortlisted",
  ASSESSMENT: "Assessment",
  INTERVIEW: "Interview",
  SELECTED: "Selected",
  OFFER_RELEASED: "Offer Released",
  ACCEPTED: "Accepted",
  REJECTED: "Rejected",
  WITHDRAWN: "Withdrawn",
};

export const TERMINAL_APPLICATION_STATUSES: ApplicationStatus[] = [
  "ACCEPTED",
  "REJECTED",
  "WITHDRAWN",
];

export const DEFAULT_FILTERS = {
  search: "",
  employmentType: null,
  location: null,
  mode: null,
  ctcMin: null,
  ctcMax: null,
  departmentId: null,
  applicationStatus: null,
} as const;

export const BACKEND_LIMITATIONS = {
  noQuestionsList:
    "Custom application questions cannot be loaded. Apply with your active resume only until question endpoints are added.",
  noCompanyNames:
    "Company names are not exposed to students. The posting title is shown instead.",
} as const;
