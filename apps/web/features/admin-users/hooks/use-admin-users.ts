"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  bulkUpdateAdminUsers,
  fetchAdminUser,
  fetchAdminUserAudit,
  fetchAdminUsers,
  updateAdminUser,
  updateAdminUserRoles,
} from "@/features/admin-users/api/admin-users-client";
import type { AdminUserFilters } from "@/features/admin-users/types";
import { useAuth } from "@/providers/auth-provider";

export const adminUserKeys = {
  all: ["admin-users"] as const,
  list: (filters: AdminUserFilters) =>
    [...adminUserKeys.all, "list", filters] as const,
  detail: (id: string) => [...adminUserKeys.all, "detail", id] as const,
  audit: (id: string) => [...adminUserKeys.all, "audit", id] as const,
};

export function useAdminUsers(filters: AdminUserFilters) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminUserKeys.list(filters),
    queryFn: () => fetchAdminUsers(filters),
    enabled: isAuthenticated,
    placeholderData: (prev) => prev,
  });
}

export function useAdminUser(id: string | null) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminUserKeys.detail(id ?? ""),
    queryFn: () => fetchAdminUser(id!),
    enabled: isAuthenticated && Boolean(id),
  });
}

export function useAdminUserAudit(id: string | null) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminUserKeys.audit(id ?? ""),
    queryFn: () => fetchAdminUserAudit(id!),
    enabled: isAuthenticated && Boolean(id),
  });
}

export function useAdminUserMutations() {
  const queryClient = useQueryClient();
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: adminUserKeys.all });

  return {
    updateUser: useMutation({
      mutationFn: ({
        id,
        payload,
      }: {
        id: string;
        payload: Parameters<typeof updateAdminUser>[1];
      }) => updateAdminUser(id, payload),
      onSuccess: () => void invalidate(),
    }),
    updateRoles: useMutation({
      mutationFn: ({
        id,
        payload,
      }: {
        id: string;
        payload: Parameters<typeof updateAdminUserRoles>[1];
      }) => updateAdminUserRoles(id, payload),
      onSuccess: () => void invalidate(),
    }),
    bulk: useMutation({
      mutationFn: bulkUpdateAdminUsers,
      onSuccess: () => void invalidate(),
    }),
  };
}
