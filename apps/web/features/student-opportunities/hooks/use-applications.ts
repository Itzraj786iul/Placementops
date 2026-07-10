"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  applyToOpportunity,
  fetchApplication,
  fetchMyApplications,
  withdrawApplication,
} from "@/features/student-opportunities/api/application-client";
import type {
  ApplyPayload,
  ApplicationListItem,
} from "@/features/student-opportunities/types";
import { opportunityQueryKeys } from "@/features/student-opportunities/hooks/use-opportunities";

export const applicationQueryKeys = {
  all: ["applications"] as const,
  me: () => ["applications", "me"] as const,
  detail: (id: string) => ["applications", "detail", id] as const,
};

export function useMyApplications() {
  return useQuery({
    queryKey: applicationQueryKeys.me(),
    queryFn: fetchMyApplications,
    staleTime: 30_000,
  });
}

export function useApplicationDetail(id: string | null, enabled = true) {
  return useQuery({
    queryKey: applicationQueryKeys.detail(id ?? ""),
    queryFn: () => fetchApplication(id!),
    enabled: Boolean(id) && enabled,
  });
}

export function useApplicationMutations() {
  const queryClient = useQueryClient();

  const invalidate = async (opportunityId?: string) => {
    await queryClient.invalidateQueries({ queryKey: applicationQueryKeys.all });
    if (opportunityId) {
      await queryClient.invalidateQueries({
        queryKey: opportunityQueryKeys.detail(opportunityId),
      });
    }
  };

  const apply = useMutation({
    mutationFn: ({
      opportunityId,
      payload,
    }: {
      opportunityId: string;
      payload: ApplyPayload;
    }) => applyToOpportunity(opportunityId, payload),
    onMutate: async ({ opportunityId, payload }) => {
      await queryClient.cancelQueries({ queryKey: applicationQueryKeys.me() });
      const previous = queryClient.getQueryData<ApplicationListItem[]>(
        applicationQueryKeys.me(),
      );
      const optimistic: ApplicationListItem = {
        id: `optimistic-${opportunityId}`,
        student_profile_id: "",
        hiring_opportunity_id: opportunityId,
        selected_resume_id: payload.selected_resume_id,
        status: "APPLIED",
        applied_at: new Date().toISOString(),
        withdrawn_at: null,
      };
      queryClient.setQueryData<ApplicationListItem[]>(
        applicationQueryKeys.me(),
        (old) => [
          ...(old ?? []).filter(
            (a) => a.hiring_opportunity_id !== opportunityId,
          ),
          optimistic,
        ],
      );
      return { previous };
    },
    onError: (_err, _vars, context) => {
      if (context?.previous) {
        queryClient.setQueryData(applicationQueryKeys.me(), context.previous);
      }
    },
    onSuccess: (_, { opportunityId }) => invalidate(opportunityId),
  });

  const withdraw = useMutation({
    mutationFn: ({
      applicationId,
      opportunityId,
    }: {
      applicationId: string;
      opportunityId: string;
    }) =>
      withdrawApplication(applicationId).then((result) => ({
        result,
        opportunityId,
      })),
    onSuccess: async ({ opportunityId }) => invalidate(opportunityId),
  });

  return { apply, withdraw };
}
