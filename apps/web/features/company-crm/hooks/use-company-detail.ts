"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchCompany } from "@/features/company-crm/api/company-client";
import { companyQueryKeys } from "@/features/company-crm/hooks/use-companies";

export function useCompanyDetail(companyId: string | null) {
  return useQuery({
    queryKey: companyQueryKeys.detail(companyId ?? ""),
    queryFn: () => fetchCompany(companyId!),
    enabled: Boolean(companyId),
  });
}
