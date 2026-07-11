"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchFeatureFlags,
  patchFeatureFlag,
} from "@/features/admin-feature-flags/api/feature-flags-client";
import { useAuth } from "@/providers/auth-provider";

export const featureFlagKeys = {
  all: ["admin-feature-flags"] as const,
  list: (search?: string) => [...featureFlagKeys.all, search ?? ""] as const,
};

export function useFeatureFlags(search?: string) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: featureFlagKeys.list(search),
    queryFn: () => fetchFeatureFlags({ search: search || undefined }),
    enabled: isAuthenticated,
    placeholderData: (prev) => prev,
  });
}

export function usePatchFeatureFlag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ key, enabled }: { key: string; enabled: boolean }) =>
      patchFeatureFlag(key, {
        enabled,
        confirm: true,
      }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: featureFlagKeys.all });
    },
  });
}
