"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchAdminSettings,
  patchAdminSettings,
} from "@/features/admin-settings/api/admin-settings-client";
import { useAuth } from "@/providers/auth-provider";

export const adminSettingsKeys = {
  all: ["admin-settings"] as const,
};

export function useAdminSettings() {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminSettingsKeys.all,
    queryFn: fetchAdminSettings,
    enabled: isAuthenticated,
  });
}

export function usePatchAdminSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchAdminSettings,
    onSuccess: (data) => {
      queryClient.setQueryData(adminSettingsKeys.all, data);
    },
  });
}
