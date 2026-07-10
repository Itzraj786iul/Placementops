"use client";

import { useQueries, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchEligibility,
  fetchOpportunities,
  fetchOpportunity,
} from "@/features/student-opportunities/api/opportunity-client";

export const opportunityQueryKeys = {
  all: ["opportunities"] as const,
  list: () => ["opportunities", "list"] as const,
  detail: (id: string) => ["opportunities", "detail", id] as const,
  eligibility: (id: string) => ["opportunities", "eligibility", id] as const,
};

export function useOpportunitiesList() {
  return useQuery({
    queryKey: opportunityQueryKeys.list(),
    queryFn: fetchOpportunities,
    staleTime: 60_000,
  });
}

export function useOpportunityDetail(id: string | null, enabled = true) {
  return useQuery({
    queryKey: opportunityQueryKeys.detail(id ?? ""),
    queryFn: () => fetchOpportunity(id!),
    enabled: Boolean(id) && enabled,
    staleTime: 60_000,
  });
}

export function useOpportunityEligibility(id: string | null, enabled = true) {
  return useQuery({
    queryKey: opportunityQueryKeys.eligibility(id ?? ""),
    queryFn: () => fetchEligibility(id!),
    enabled: Boolean(id) && enabled,
    staleTime: 60_000,
  });
}

export function useOpportunityDetailsBatch(ids: string[]) {
  return useQueries({
    queries: ids.map((id) => ({
      queryKey: opportunityQueryKeys.detail(id),
      queryFn: () => fetchOpportunity(id),
      staleTime: 5 * 60_000,
      enabled: Boolean(id),
    })),
  });
}

export function useInvalidateOpportunities() {
  const queryClient = useQueryClient();

  return {
    invalidateAll: async () => {
      await queryClient.invalidateQueries({
        queryKey: opportunityQueryKeys.all,
      });
    },
    invalidateDetail: async (id: string) => {
      await queryClient.invalidateQueries({
        queryKey: opportunityQueryKeys.detail(id),
      });
    },
  };
}

export function usePrefetchOpportunity() {
  const queryClient = useQueryClient();

  return (id: string) => {
    void queryClient.prefetchQuery({
      queryKey: opportunityQueryKeys.detail(id),
      queryFn: () => fetchOpportunity(id),
      staleTime: 60_000,
    });
  };
}

export function useEligibilityBatch(ids: string[], enabled = true) {
  return useQueries({
    queries: ids.map((id) => ({
      queryKey: opportunityQueryKeys.eligibility(id),
      queryFn: () => fetchEligibility(id),
      staleTime: 5 * 60_000,
      enabled: enabled && Boolean(id),
    })),
  });
}
