"use client";

import { usePathname, useRouter } from "next/navigation";
import * as React from "react";

import { AUTH_ROUTES, PUBLIC_ROUTES } from "@/lib/auth/constants";
import { getWorkspacePathForUser } from "@/lib/auth/redirects";
import { useAuth } from "@/providers/auth-provider";

type RouteGuardProps = {
  children: React.ReactNode;
};

function isPublicRoute(pathname: string): boolean {
  return (
    PUBLIC_ROUTES.includes(pathname as (typeof PUBLIC_ROUTES)[number]) ||
    AUTH_ROUTES.some((route) => pathname.startsWith(route))
  );
}

export function RouteGuard({ children }: RouteGuardProps) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  React.useEffect(() => {
    if (isLoading) return;

    if (
      (pathname === "/login" || pathname === "/signup") &&
      isAuthenticated &&
      user
    ) {
      router.replace(getWorkspacePathForUser(user));
      return;
    }

    if (!isPublicRoute(pathname) && !isAuthenticated) {
      const loginUrl = `/login?redirect=${encodeURIComponent(pathname)}`;
      router.replace(loginUrl);
    }
  }, [isLoading, isAuthenticated, user, pathname, router]);

  if (isLoading && !isPublicRoute(pathname)) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="border-primary h-8 w-8 animate-spin rounded-full border-4 border-t-transparent" />
      </div>
    );
  }

  return <>{children}</>;
}
