"use client";

import { useQuery } from "@tanstack/react-query";

import { fetchSystemHealth } from "@/features/admin-health/api/admin-health-client";
import { useAuth } from "@/providers/auth-provider";

export const adminHealthKeys = {
  all: ["admin-system-health"] as const,
};

export function useSystemHealth() {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: adminHealthKeys.all,
    queryFn: fetchSystemHealth,
    enabled: isAuthenticated,
    refetchInterval: 60_000,
    staleTime: 15_000,
  });
}
