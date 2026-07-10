import { apiRequest } from "@/lib/api-client";
import type {
  Company,
  CompanyContact,
  CompanyDocument,
  CompanyListItem,
  CompanyPipeline,
  CompanyStatus,
  TimelineEntry,
} from "@/features/company-crm/types";

export async function fetchCompanies(
  status?: CompanyStatus,
): Promise<CompanyListItem[]> {
  const query = status ? `?status=${status}` : "";
  return apiRequest<CompanyListItem[]>(`/companies${query}`);
}

export async function fetchCompany(id: string): Promise<Company> {
  return apiRequest<Company>(`/companies/${id}`);
}

export async function createCompany(payload: {
  name: string;
  industry?: string | null;
  website?: string | null;
  linkedin?: string | null;
  headquarters?: string | null;
  company_type?: string | null;
  handler?: {
    handler_user_id: string;
    branch?: string | null;
    ownership_type: string;
  };
}): Promise<Company> {
  return apiRequest<Company>("/companies", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateCompany(
  id: string,
  payload: Partial<{
    name: string;
    industry: string | null;
    website: string | null;
    linkedin: string | null;
    headquarters: string | null;
    company_type: string | null;
    status: CompanyStatus;
    handler: {
      handler_user_id: string;
      branch?: string | null;
      ownership_type: string;
    };
  }>,
): Promise<Company> {
  return apiRequest<Company>(`/companies/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchContacts(
  companyId: string,
): Promise<CompanyContact[]> {
  return apiRequest<CompanyContact[]>(`/companies/${companyId}/contacts`);
}

export async function createContact(
  companyId: string,
  payload: {
    name: string;
    designation?: string | null;
    email?: string | null;
    phone?: string | null;
    linkedin?: string | null;
    is_primary: boolean;
    notes?: string | null;
  },
): Promise<CompanyContact> {
  return apiRequest<CompanyContact>(`/companies/${companyId}/contacts`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchTimeline(
  companyId: string,
): Promise<TimelineEntry[]> {
  return apiRequest<TimelineEntry[]>(`/companies/${companyId}/timeline`);
}

export async function createCommunication(
  companyId: string,
  payload: {
    type: string;
    subject?: string | null;
    description: string;
    communication_date: string;
  },
): Promise<TimelineEntry> {
  return apiRequest<TimelineEntry>(`/companies/${companyId}/communications`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updatePipeline(
  companyId: string,
  payload: { current_stage: string },
): Promise<CompanyPipeline> {
  return apiRequest<CompanyPipeline>(`/companies/${companyId}/pipeline`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function createDocument(
  companyId: string,
  payload: { document_type: string; file_url: string },
): Promise<CompanyDocument> {
  return apiRequest<CompanyDocument>(`/companies/${companyId}/documents`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function uploadDocument(
  companyId: string,
  file: File,
  documentType: string,
  onProgress: (pct: number) => void = () => undefined,
): Promise<CompanyDocument> {
  const { uploadWithProgress, parseUploadError } =
    await import("@/components/ui/file-upload");
  const form = new FormData();
  form.append("file", file);
  form.append("document_type", documentType);
  const response = await uploadWithProgress(
    `/api/v1/companies/${companyId}/documents/upload`,
    form,
    onProgress,
  );
  if (!response.ok) {
    throw new Error(await parseUploadError(response));
  }
  return response.json() as Promise<CompanyDocument>;
}
