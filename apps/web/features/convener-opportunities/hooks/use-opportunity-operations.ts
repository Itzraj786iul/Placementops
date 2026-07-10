"use client";

import { useQueries, useQuery } from "@tanstack/react-query";

import {
  fetchApplicationSnapshot,
  fetchCompanyName,
  fetchEligibility,
  fetchOpportunity,
  fetchOpportunityApplications,
  fetchOpportunityTimeline,
} from "@/features/convener-opportunities/api/operations-client";

export const operationsQueryKeys = {
  all: ["convener-opportunities"] as const,
  opportunity: (id: string) =>
    ["convener-opportunities", "opportunity", id] as const,
  companyName: (companyId: string) =>
    ["convener-opportunities", "company-name", companyId] as const,
  eligibility: (id: string) =>
    ["convener-opportunities", "eligibility", id] as const,
  timeline: (id: string) => ["convener-opportunities", "timeline", id] as const,
  applications: (id: string) =>
    ["convener-opportunities", "applications", id] as const,
  snapshot: (applicationId: string) =>
    ["convener-opportunities", "snapshot", applicationId] as const,
};

export function useOpportunityOperations(opportunityId: string) {
  const opportunity = useQuery({
    queryKey: operationsQueryKeys.opportunity(opportunityId),
    queryFn: () => fetchOpportunity(opportunityId),
    staleTime: 2 * 60_000,
  });

  const companyName = useQuery({
    queryKey: operationsQueryKeys.companyName(
      opportunity.data?.company_id ?? "",
    ),
    queryFn: () => fetchCompanyName(opportunity.data!.company_id),
    enabled: Boolean(opportunity.data?.company_id),
    staleTime: 10 * 60_000,
  });

  return { opportunity, companyName };
}

export function useOpportunityEligibility(
  opportunityId: string,
  enabled = true,
) {
  return useQuery({
    queryKey: operationsQueryKeys.eligibility(opportunityId),
    queryFn: () => fetchEligibility(opportunityId),
    enabled,
    staleTime: 5 * 60_000,
  });
}

export function useOpportunityTimeline(opportunityId: string, enabled = true) {
  return useQuery({
    queryKey: operationsQueryKeys.timeline(opportunityId),
    queryFn: () => fetchOpportunityTimeline(opportunityId),
    enabled,
    staleTime: 60_000,
  });
}

export function useOpportunityApplications(
  opportunityId: string,
  enabled = true,
) {
  return useQuery({
    queryKey: operationsQueryKeys.applications(opportunityId),
    queryFn: () => fetchOpportunityApplications(opportunityId),
    enabled,
    staleTime: 30_000,
  });
}

export function useApplicationSnapshots(
  applicationIds: string[],
  enabled = true,
) {
  return useQueries({
    queries: applicationIds.map((id) => ({
      queryKey: operationsQueryKeys.snapshot(id),
      queryFn: () => fetchApplicationSnapshot(id),
      enabled: enabled && Boolean(id),
      staleTime: 5 * 60_000,
    })),
  });
}
