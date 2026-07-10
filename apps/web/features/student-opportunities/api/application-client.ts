import type {
  ApplicationDetail,
  ApplicationListItem,
  ApplyPayload,
} from "@/features/student-opportunities/types";
import { apiRequest } from "@/lib/api-client";

export async function fetchMyApplications(): Promise<ApplicationListItem[]> {
  return apiRequest<ApplicationListItem[]>("/applications/me");
}

export async function fetchApplication(id: string): Promise<ApplicationDetail> {
  return apiRequest<ApplicationDetail>(`/applications/${id}`);
}

export async function applyToOpportunity(
  opportunityId: string,
  payload: ApplyPayload,
): Promise<ApplicationDetail> {
  return apiRequest<ApplicationDetail>(
    `/opportunities/${opportunityId}/apply`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export async function withdrawApplication(
  applicationId: string,
): Promise<ApplicationDetail> {
  return apiRequest<ApplicationDetail>(
    `/applications/${applicationId}/withdraw`,
    { method: "POST" },
  );
}
