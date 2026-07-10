"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  createCompany,
  fetchCompanies,
  updateCompany,
} from "@/features/company-crm/api/company-client";
import type { CompanyStatus } from "@/features/company-crm/types";

export const companyQueryKeys = {
  all: ["companies"] as const,
  list: (status?: CompanyStatus) =>
    ["companies", "list", status ?? "all"] as const,
  detail: (id: string) => ["companies", "detail", id] as const,
  contacts: (id: string) => ["companies", "contacts", id] as const,
  timeline: (id: string) => ["companies", "timeline", id] as const,
  documents: (id: string) => ["companies", "documents", id] as const,
};

export function useCompaniesList() {
  return useQuery({
    queryKey: companyQueryKeys.list(),
    queryFn: () => fetchCompanies(),
  });
}

export function useCompanyMutations() {
  const queryClient = useQueryClient();

  const invalidate = async (companyId?: string) => {
    await queryClient.invalidateQueries({ queryKey: companyQueryKeys.all });
    if (companyId) {
      await queryClient.invalidateQueries({
        queryKey: companyQueryKeys.detail(companyId),
      });
    }
  };

  const create = useMutation({
    mutationFn: createCompany,
    onSuccess: () => invalidate(),
  });

  const update = useMutation({
    mutationFn: ({
      id,
      payload,
    }: {
      id: string;
      payload: Parameters<typeof updateCompany>[1];
    }) => updateCompany(id, payload),
    onSuccess: (_, { id }) => invalidate(id),
  });

  return { create, update, invalidate };
}
