import type {
  ApplicationStatus,
  TimelineStage,
} from "@/features/student-opportunities/types";

export const CONVENER_STAFF_ROLES = [
  "PLACEMENT_CONVENER",
  "PLACEMENT_CELL",
  "SUPER_ADMIN",
] as const;

export const OPPORTUNITY_STATUS_LABELS: Record<string, string> = {
  DRAFT: "Draft",
  PUBLISHED: "Published",
  ARCHIVED: "Archived",
};

export const TIMELINE_STAGE_LABELS: Record<TimelineStage, string> = {
  DRAFT: "Draft",
  PUBLISHED: "Published",
  APPLICATIONS_OPEN: "Applications Open",
  APPLICATIONS_CLOSED: "Applications Closed",
  SHORTLIST_RELEASED: "Shortlist",
  ASSESSMENT: "Assessment",
  INTERVIEW: "Interview",
  SELECTED: "Selected",
  OFFER_RELEASED: "Offer",
  COMPLETED: "Completed",
};

export const TIMELINE_STAGES_ORDER: TimelineStage[] = [
  "DRAFT",
  "PUBLISHED",
  "APPLICATIONS_OPEN",
  "APPLICATIONS_CLOSED",
  "SHORTLIST_RELEASED",
  "ASSESSMENT",
  "INTERVIEW",
  "SELECTED",
  "OFFER_RELEASED",
  "COMPLETED",
];

export const DEFAULT_APPLICATION_FILTERS = {
  search: "",
  status: null,
  department: null,
  branch: null,
} as const;

export const APPLICATIONS_PAGE_SIZE = 10;

export const BACKEND_LIMITATIONS = {
  noApplicationQuestions:
    "Application question definitions cannot be loaded. Answer text is shown when present on the application detail.",
  listLacksStudentFields:
    "Application list rows only include IDs. Student display fields are loaded from application snapshots.",
  remarksNotPersisted:
    "Status update remarks are accepted by the API but not persisted yet.",
} as const;

export const APPLICATION_STATUS_OPTIONS: ApplicationStatus[] = [
  "APPLIED",
  "UNDER_REVIEW",
  "SHORTLISTED",
  "ASSESSMENT",
  "INTERVIEW",
  "SELECTED",
  "OFFER_RELEASED",
  "ACCEPTED",
  "REJECTED",
  "WITHDRAWN",
];
