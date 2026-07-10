import type {
  ApplicationDetail,
  ApplicationSnapshot,
  TimelineEntry,
} from "@/features/convener-opportunities/types";
import type {
  EligibilityRule,
  OpportunityDetail,
} from "@/features/student-opportunities/types";
import { apiRequest } from "@/lib/api-client";
import type { ApplicationListItem } from "@/features/student-opportunities/types";

export async function fetchOpportunityApplications(
  opportunityId: string,
): Promise<ApplicationListItem[]> {
  return apiRequest<ApplicationListItem[]>(
    `/opportunities/${opportunityId}/applications`,
  );
}

export async function fetchOpportunityTimeline(
  opportunityId: string,
): Promise<TimelineEntry[]> {
  return apiRequest<TimelineEntry[]>(
    `/opportunities/${opportunityId}/timeline`,
  );
}

export async function fetchApplicationDetail(
  applicationId: string,
): Promise<ApplicationDetail> {
  return apiRequest<ApplicationDetail>(`/applications/${applicationId}`);
}

export async function fetchApplicationSnapshot(
  applicationId: string,
): Promise<ApplicationSnapshot> {
  return apiRequest<ApplicationSnapshot>(
    `/applications/${applicationId}/snapshot`,
  );
}

export async function fetchOpportunity(id: string): Promise<OpportunityDetail> {
  return apiRequest<OpportunityDetail>(`/opportunities/${id}`);
}

export async function fetchEligibility(id: string): Promise<EligibilityRule> {
  return apiRequest<EligibilityRule>(`/opportunities/${id}/eligibility`);
}

export async function fetchCompanyName(companyId: string): Promise<string> {
  const company = await apiRequest<{ name: string }>(`/companies/${companyId}`);
  return company.name;
}
