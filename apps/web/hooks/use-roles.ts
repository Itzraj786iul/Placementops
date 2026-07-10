"use client";

import type { RoleName } from "@placementos/types";

import { hasAnyRole, hasRole } from "@/lib/auth/roles";
import { useAuth } from "@/providers/auth-provider";

export function useHasRole(role: RoleName): boolean {
  const { user } = useAuth();
  return hasRole(user, role);
}

export function useHasAnyRole(roles: RoleName[]): boolean {
  const { user } = useAuth();
  return hasAnyRole(user, roles);
}
