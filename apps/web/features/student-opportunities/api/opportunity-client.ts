import type {
  EligibilityRule,
  OpportunityDetail,
  OpportunityListItem,
} from "@/features/student-opportunities/types";
import { apiRequest } from "@/lib/api-client";

export async function fetchOpportunities(): Promise<OpportunityListItem[]> {
  return apiRequest<OpportunityListItem[]>("/opportunities");
}

export async function fetchOpportunity(id: string): Promise<OpportunityDetail> {
  return apiRequest<OpportunityDetail>(`/opportunities/${id}`);
}

export async function fetchEligibility(id: string): Promise<EligibilityRule> {
  return apiRequest<EligibilityRule>(`/opportunities/${id}/eligibility`);
}
