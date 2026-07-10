import type {
  CommunicationType,
  CompanyDocumentType,
  CompanyStatus,
  OwnershipType,
  PipelineStage,
} from "@/features/company-crm/types";

export const PIPELINE_STAGES: PipelineStage[] = [
  "NOT_CONTACTED",
  "INVITATION_SENT",
  "FOLLOW_UP_PENDING",
  "HR_REPLIED",
  "MEETING_SCHEDULED",
  "INTERESTED",
  "ON_HOLD",
  "REJECTED",
  "DRIVE_PLANNED",
];

export const PIPELINE_LABELS: Record<PipelineStage, string> = {
  NOT_CONTACTED: "Not Contacted",
  INVITATION_SENT: "Invitation Sent",
  FOLLOW_UP_PENDING: "Follow-up Pending",
  HR_REPLIED: "HR Replied",
  MEETING_SCHEDULED: "Meeting Scheduled",
  INTERESTED: "Interested",
  ON_HOLD: "On Hold",
  REJECTED: "Rejected",
  DRIVE_PLANNED: "Drive Planned",
};

export const COMPANY_STATUSES: CompanyStatus[] = ["ACTIVE", "INACTIVE"];

export const OWNERSHIP_TYPES: OwnershipType[] = [
  "LEGACY",
  "NEW",
  "TRANSFERRED",
];

export const OWNERSHIP_LABELS: Record<OwnershipType, string> = {
  LEGACY: "Legacy",
  NEW: "New",
  TRANSFERRED: "Transferred",
};

export const COMMUNICATION_TYPES: CommunicationType[] = [
  "EMAIL",
  "CALL",
  "MEETING",
  "WHATSAPP",
  "OTHER",
];

export const DOCUMENT_TYPES: CompanyDocumentType[] = [
  "JD",
  "ELIGIBILITY",
  "PPT",
  "OFFER_TEMPLATE",
  "BOND",
  "OTHER",
];

export const DOCUMENT_LABELS: Record<CompanyDocumentType, string> = {
  JD: "Job Description",
  ELIGIBILITY: "Eligibility",
  PPT: "Presentation",
  OFFER_TEMPLATE: "Offer Template",
  BOND: "Bond",
  OTHER: "Other",
};

export const CRM_STAFF_ROLES = [
  "PLACEMENT_CONVENER",
  "PLACEMENT_CELL",
  "SUPER_ADMIN",
] as const;

export const DEFAULT_FILTERS = {
  search: "",
  handlerId: null,
  industry: null,
  status: null,
  pipelineStage: null,
  ownershipType: null,
};
