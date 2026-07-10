"use client";

import { useQueries, useQuery } from "@tanstack/react-query";

import {
  evaluateStudentEligibility,
  fetchScreeningSummary,
} from "@/features/eligibility/api/eligibility-client";

export const eligibilityEngineKeys = {
  all: ["eligibility-engine"] as const,
  screening: (opportunityId: string) =>
    ["eligibility-engine", "screening", opportunityId] as const,
  evaluation: (opportunityId: string, studentProfileId: string) =>
    [
      "eligibility-engine",
      "evaluation",
      opportunityId,
      studentProfileId,
    ] as const,
};

export function useScreeningSummary(
  opportunityId: string | null,
  enabled = true,
) {
  return useQuery({
    queryKey: eligibilityEngineKeys.screening(opportunityId ?? ""),
    queryFn: () => fetchScreeningSummary(opportunityId!),
    enabled: Boolean(opportunityId) && enabled,
    staleTime: 60_000,
  });
}

export function useStudentEligibilityEvaluation(
  opportunityId: string | null,
  studentProfileId: string | null | undefined,
  enabled = true,
) {
  return useQuery({
    queryKey: eligibilityEngineKeys.evaluation(
      opportunityId ?? "",
      studentProfileId ?? "",
    ),
    queryFn: () =>
      evaluateStudentEligibility(opportunityId!, studentProfileId!),
    enabled: Boolean(opportunityId) && Boolean(studentProfileId) && enabled,
    staleTime: 60_000,
  });
}

export function useStudentEligibilityBatch(
  opportunityIds: string[],
  studentProfileId: string | null | undefined,
  enabled = true,
) {
  return useQueries({
    queries: opportunityIds.map((opportunityId) => ({
      queryKey: eligibilityEngineKeys.evaluation(
        opportunityId,
        studentProfileId ?? "",
      ),
      queryFn: () =>
        evaluateStudentEligibility(opportunityId, studentProfileId!),
      enabled: enabled && Boolean(opportunityId) && Boolean(studentProfileId),
      staleTime: 5 * 60_000,
    })),
  });
}
