"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createContact,
  fetchContacts,
} from "@/features/company-crm/api/company-client";
import { companyQueryKeys } from "@/features/company-crm/hooks/use-companies";

export function useCompanyContacts(companyId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: companyQueryKeys.contacts(companyId ?? ""),
    queryFn: () => fetchContacts(companyId!),
    enabled: Boolean(companyId) && enabled,
  });
}

export function useCreateContact(companyId: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload: Parameters<typeof createContact>[1]) =>
      createContact(companyId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey: companyQueryKeys.contacts(companyId),
      });
    },
  });
}
