"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  activateAdminSeason,
  createAdminDepartment,
  createAdminSeason,
  fetchAdminDepartments,
  fetchAdminSeasons,
  updateAdminDepartment,
  updateAdminSeason,
} from "@/features/admin-org/api/admin-org-client";
import { useAuth } from "@/providers/auth-provider";

export const adminOrgKeys = {
  all: ["admin-org"] as const,
  departments: (params: object) =>
    [...adminOrgKeys.all, "departments", params] as const,
  seasons: (params: object) =>
    [...adminOrgKeys.all, "seasons", params] as const,
};

export function useAdminDepartments(params: {
  search?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminOrgKeys.departments(params),
    queryFn: () => fetchAdminDepartments(params),
    enabled: isAuthenticated,
    placeholderData: (prev) => prev,
  });
}

export function useAdminSeasons(params: {
  search?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminOrgKeys.seasons(params),
    queryFn: () => fetchAdminSeasons(params),
    enabled: isAuthenticated,
    placeholderData: (prev) => prev,
  });
}

export function useAdminOrgMutations() {
  const queryClient = useQueryClient();
  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: adminOrgKeys.all });

  return {
    createDepartment: useMutation({
      mutationFn: createAdminDepartment,
      onSuccess: () => void invalidate(),
    }),
    updateDepartment: useMutation({
      mutationFn: ({
        id,
        payload,
      }: {
        id: string;
        payload: Parameters<typeof updateAdminDepartment>[1];
      }) => updateAdminDepartment(id, payload),
      onSuccess: () => void invalidate(),
    }),
    createSeason: useMutation({
      mutationFn: createAdminSeason,
      onSuccess: () => void invalidate(),
    }),
    updateSeason: useMutation({
      mutationFn: ({
        id,
        payload,
      }: {
        id: string;
        payload: Parameters<typeof updateAdminSeason>[1];
      }) => updateAdminSeason(id, payload),
      onSuccess: () => void invalidate(),
    }),
    activateSeason: useMutation({
      mutationFn: activateAdminSeason,
      onSuccess: () => void invalidate(),
    }),
  };
}
