export type CompanyStatus = "ACTIVE" | "INACTIVE";

export type OwnershipType = "LEGACY" | "NEW" | "TRANSFERRED";

export type PipelineStage =
  | "NOT_CONTACTED"
  | "INVITATION_SENT"
  | "FOLLOW_UP_PENDING"
  | "HR_REPLIED"
  | "MEETING_SCHEDULED"
  | "INTERESTED"
  | "ON_HOLD"
  | "REJECTED"
  | "DRIVE_PLANNED";

export type CommunicationType =
  "EMAIL" | "CALL" | "MEETING" | "WHATSAPP" | "OTHER";

export type CompanyDocumentType =
  "JD" | "ELIGIBILITY" | "PPT" | "OFFER_TEMPLATE" | "BOND" | "OTHER";

export type CompanyHandler = {
  id: string;
  company_id: string;
  handler_user_id: string;
  branch: string | null;
  ownership_type: OwnershipType;
  assigned_by: string;
  assigned_at: string;
  ended_at: string | null;
  is_active: boolean;
};

export type CompanyPipeline = {
  id: string;
  company_id: string;
  current_stage: PipelineStage;
  last_updated: string;
  updated_by: string;
};

export type CompanyListItem = {
  id: string;
  name: string;
  industry: string | null;
  company_type: string | null;
  status: CompanyStatus;
  created_at: string;
  pipeline: CompanyPipeline | null;
  active_handler: CompanyHandler | null;
};

export type Company = CompanyListItem & {
  website: string | null;
  linkedin: string | null;
  headquarters: string | null;
  created_by: string;
  updated_at: string;
};

export type CompanyContact = {
  id: string;
  company_id: string;
  name: string;
  designation: string | null;
  email: string | null;
  phone: string | null;
  linkedin: string | null;
  is_primary: boolean;
  notes: string | null;
};

export type TimelineEntry = {
  id: string;
  type: CommunicationType;
  subject: string | null;
  description: string;
  communication_date: string;
  created_by: string;
  created_at: string;
};

export type CompanyDocument = {
  id: string;
  company_id: string;
  document_type: CompanyDocumentType;
  file_url: string;
  uploaded_by: string;
  uploaded_at: string;
};

export type CrmTab =
  "overview" | "contacts" | "timeline" | "documents" | "history";

export type CompanyFilters = {
  search: string;
  handlerId: string | null;
  industry: string | null;
  status: CompanyStatus | null;
  pipelineStage: PipelineStage | null;
  ownershipType: OwnershipType | null;
};
