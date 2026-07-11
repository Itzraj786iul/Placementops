"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { useSystemHealth } from "@/features/admin-health/hooks/use-admin-health";
import type {
  ComponentStatus,
  HealthLevel,
} from "@/features/admin-health/api/admin-health-client";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, string> = {
  healthy: "border-emerald-500/40 bg-emerald-500/10 text-emerald-800",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-900",
  critical: "border-red-500/40 bg-red-500/10 text-red-800",
  unknown: "border-muted bg-muted text-muted-foreground",
  skipped: "border-muted bg-muted text-muted-foreground",
};

const DOT: Record<string, string> = {
  healthy: "bg-emerald-500",
  warning: "bg-amber-500",
  critical: "bg-red-500",
  unknown: "bg-slate-400",
  skipped: "bg-slate-400",
};

function formatUptime(seconds: number) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = seconds % 60;
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function StatusBadge({ status }: { status: ComponentStatus | HealthLevel }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
        STATUS_STYLES[status] ?? STATUS_STYLES.unknown,
      )}
    >
      <span
        className={cn("h-1.5 w-1.5 rounded-full", DOT[status] ?? DOT.unknown)}
      />
      {status}
    </span>
  );
}

function Card({
  title,
  status,
  children,
}: {
  title: string;
  status: ComponentStatus | HealthLevel;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-lg border p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <h2 className="text-sm font-semibold">{title}</h2>
        <StatusBadge status={status} />
      </div>
      <div className="space-y-2 text-sm">{children}</div>
    </section>
  );
}

function Row({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="flex items-start justify-between gap-3">
      <span className="text-muted-foreground text-xs">{label}</span>
      <span className="text-right text-xs font-medium">{value ?? "—"}</span>
    </div>
  );
}

function SkeletonGrid() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="bg-muted h-40 animate-pulse rounded-lg" />
      ))}
    </div>
  );
}

export function SystemHealthWorkspace() {
  const query = useSystemHealth();
  const data = query.data;

  return (
    <div className="-m-6 flex flex-col">
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">System Health</h1>
          <p className="text-muted-foreground text-xs">
            Operational status for PlacementOS. Auto-refreshes every 60s.
          </p>
        </div>
        {data && (
          <div className="flex flex-wrap items-center gap-2">
            <StatusBadge status={data.overall_status} />
            <span className="text-muted-foreground text-xs">
              {data.check_duration_ms.toFixed(0)} ms
              {data.cached ? " · cached" : ""}
            </span>
          </div>
        )}
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={query.isFetching}
          onClick={() => void query.refetch()}
        >
          {query.isFetching ? "Refreshing…" : "Refresh"}
        </Button>
      </header>

      <div className="space-y-6 p-4 md:p-6">
        {query.isLoading && <SkeletonGrid />}

        {query.isError && (
          <p className="text-destructive text-sm">
            {query.error instanceof Error
              ? query.error.message
              : "Failed to load system health"}
          </p>
        )}

        {data && (
          <>
            <section
              className={cn(
                "rounded-lg border p-5",
                STATUS_STYLES[data.overall_status],
              )}
            >
              <p className="text-xs tracking-wide uppercase opacity-80">
                Overall system status
              </p>
              <p className="mt-1 text-2xl font-semibold capitalize">
                {data.overall_status}
              </p>
              <p className="mt-1 text-xs opacity-80">
                Checked {new Date(data.checked_at).toLocaleString()}
              </p>
            </section>

            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
              <Card title="Database" status={data.database.status}>
                <Row
                  label="Connection"
                  value={data.database.connected ? "Connected" : "Down"}
                />
                <Row
                  label="Response time"
                  value={
                    data.database.response_time_ms != null
                      ? `${data.database.response_time_ms} ms`
                      : "—"
                  }
                />
                <Row
                  label="Migration"
                  value={data.database.migration_version}
                />
                <Row
                  label="Active connections"
                  value={data.database.active_connections}
                />
              </Card>

              <Card title="Storage" status={data.storage.status}>
                <Row label="Provider" value={data.storage.provider} />
                <Row
                  label="Configured"
                  value={data.storage.configured ? "Yes" : "No"}
                />
                <Row
                  label="Reachable"
                  value={
                    data.storage.reachable == null
                      ? "—"
                      : data.storage.reachable
                        ? "Yes"
                        : "No"
                  }
                />
                <Row label="Upload test" value={data.storage.upload_test} />
                {data.storage.detail && (
                  <p className="text-muted-foreground text-xs">
                    {data.storage.detail}
                  </p>
                )}
              </Card>

              <Card title="Email" status={data.email.status}>
                <Row label="Provider" value={data.email.provider} />
                <Row
                  label="Reachable"
                  value={
                    data.email.reachable == null
                      ? "—"
                      : data.email.reachable
                        ? "Yes"
                        : "No"
                  }
                />
                <Row label="Last send" value={data.email.last_send_status} />
                <Row label="Templates" value={data.email.template_count} />
              </Card>

              <Card title="Authentication" status={data.authentication.status}>
                <Row
                  label="Google OAuth"
                  value={
                    data.authentication.google_oauth_configured
                      ? data.authentication.google_oauth_reachable == null
                        ? "Configured"
                        : data.authentication.google_oauth_reachable
                          ? "Reachable"
                          : "Unreachable"
                      : "Not configured"
                  }
                />
                <Row label="JWT" value={data.authentication.jwt_status} />
                <Row
                  label="Session store"
                  value={data.authentication.session_store_status}
                />
              </Card>

              <Card title="Application" status={data.application.status}>
                <Row label="Version" value={data.application.version} />
                <Row label="Environment" value={data.application.environment} />
                <Row label="Build date" value={data.application.build_date} />
                <Row label="Git commit" value={data.application.git_commit} />
                <Row
                  label="Uptime"
                  value={formatUptime(data.application.uptime_seconds)}
                />
              </Card>

              <Card title="Statistics" status="healthy">
                <Row label="Users" value={data.statistics.users} />
                <Row label="Students" value={data.statistics.students} />
                <Row label="Conveners" value={data.statistics.conveners} />
                <Row label="Companies" value={data.statistics.companies} />
                <Row
                  label="Opportunities"
                  value={data.statistics.hiring_opportunities}
                />
                <Row
                  label="Applications"
                  value={data.statistics.applications}
                />
                <Row
                  label="Notifications"
                  value={data.statistics.notifications}
                />
                <Row
                  label="Storage files (approx)"
                  value={data.statistics.storage_files_approx}
                />
              </Card>
            </div>

            {data.notes.length > 0 && (
              <ul className="text-muted-foreground list-inside list-disc text-xs">
                {data.notes.map((note) => (
                  <li key={note}>{note}</li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    </div>
  );
}
