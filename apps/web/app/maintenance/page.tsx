"use client";

import * as React from "react";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { fetchPublicMaintenanceStatus } from "@/features/admin-maintenance/api/maintenance-client";
import type { MaintenanceStatus } from "@/features/admin-maintenance/api/maintenance-client";
import { APP_NAME } from "@/lib/constants";

export default function PublicMaintenancePage() {
  const [status, setStatus] = React.useState<MaintenanceStatus | null>(null);
  const [error, setError] = React.useState<string | null>(null);

  React.useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const data = await fetchPublicMaintenanceStatus();
        if (!cancelled) setStatus(data);
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Unable to load status",
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="from-background via-background to-muted/40 flex min-h-screen items-center justify-center bg-gradient-to-b px-4">
      <div className="w-full max-w-lg rounded-2xl border bg-white/80 p-8 shadow-sm backdrop-blur">
        <p className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          {APP_NAME}
        </p>
        {error && <p className="text-destructive mt-4 text-sm">{error}</p>}
        {!status && !error && (
          <div className="bg-muted mt-6 h-24 animate-pulse rounded-lg" />
        )}
        {status && (
          <>
            <h1 className="mt-3 text-2xl font-semibold tracking-tight">
              {status.enabled ? status.title : "Systems are operating normally"}
            </h1>
            <p className="text-muted-foreground mt-3 text-sm whitespace-pre-wrap">
              {status.enabled
                ? status.message
                : "Maintenance mode is not active. You can continue to the login page."}
            </p>
            {status.enabled && status.estimated_completion && (
              <p className="mt-4 text-sm">
                Estimated completion: {status.estimated_completion}
              </p>
            )}
            {status.enabled && status.support_contact && (
              <p className="mt-1 text-sm">Support: {status.support_contact}</p>
            )}
          </>
        )}
        <div className="mt-6 flex gap-2">
          <Button asChild variant="outline">
            <Link href="/login">Back to login</Link>
          </Button>
          <Button
            type="button"
            variant="ghost"
            onClick={() => window.location.reload()}
          >
            Refresh
          </Button>
        </div>
      </div>
    </main>
  );
}
