"use client";

import type { RoleName } from "@placementos/types";
import { useRouter } from "next/navigation";
import * as React from "react";

import { getWorkspacePathForUser } from "@/lib/auth/redirects";
import { hasAnyRole, hasRole } from "@/lib/auth/roles";
import { useAuth } from "@/providers/auth-provider";

type ProtectedRouteProps = {
  children: React.ReactNode;
  roles?: RoleName[];
  fallback?: React.ReactNode;
  redirectTo?: string;
};

export function ProtectedRoute({
  children,
  roles,
  fallback,
  redirectTo = "/login",
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (isLoading) return;

    if (!isAuthenticated) {
      router.replace(redirectTo);
      return;
    }

    if (roles && roles.length > 0 && !hasAnyRole(user, roles) && user) {
      router.replace(getWorkspacePathForUser(user));
    }
  }, [isLoading, isAuthenticated, user, roles, router, redirectTo]);

  if (isLoading) {
    return (
      fallback ?? (
        <div className="flex min-h-[50vh] items-center justify-center">
          <div className="border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent" />
        </div>
      )
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  if (roles && roles.length > 0 && !hasAnyRole(user, roles)) {
    return null;
  }

  return <>{children}</>;
}

type RoleGuardProps = {
  children: React.ReactNode;
  role: RoleName;
  fallback?: React.ReactNode;
};

export function RoleGuard({ children, role, fallback = null }: RoleGuardProps) {
  const { user } = useAuth();

  if (!hasRole(user, role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
