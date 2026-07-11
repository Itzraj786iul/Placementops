"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchAdminMaintenance,
  patchAdminMaintenance,
} from "@/features/admin-maintenance/api/maintenance-client";
import { useAuth } from "@/providers/auth-provider";

export const maintenanceKeys = {
  all: ["admin-maintenance"] as const,
};

export function useAdminMaintenance() {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: maintenanceKeys.all,
    queryFn: fetchAdminMaintenance,
    enabled: isAuthenticated,
  });
}

export function usePatchMaintenance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: patchAdminMaintenance,
    onSuccess: (data) => {
      queryClient.setQueryData(maintenanceKeys.all, data);
    },
  });
}
