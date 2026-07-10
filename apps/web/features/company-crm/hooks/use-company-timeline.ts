"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCommunication,
  fetchTimeline,
} from "@/features/company-crm/api/company-client";
import { companyQueryKeys } from "@/features/company-crm/hooks/use-companies";

export function useCompanyTimeline(companyId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: companyQueryKeys.timeline(companyId ?? ""),
    queryFn: () => fetchTimeline(companyId!),
    enabled: Boolean(companyId) && enabled,
  });
}

export function useCreateCommunication(companyId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof createCommunication>[1]) =>
      createCommunication(companyId, payload),
    onMutate: async (_payload) => {
      await queryClient.cancelQueries({
        queryKey: companyQueryKeys.timeline(companyId),
      });
      const previous = queryClient.getQueryData(
        companyQueryKeys.timeline(companyId),
      );
      return { previous };
    },
    onError: (_err, _payload, context) => {
      if (context?.previous) {
        queryClient.setQueryData(
          companyQueryKeys.timeline(companyId),
          context.previous,
        );
      }
    },
    onSettled: async () => {
      await queryClient.invalidateQueries({
        queryKey: companyQueryKeys.timeline(companyId),
      });
    },
  });
}
