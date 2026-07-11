"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  useFeatureFlags,
  usePatchFeatureFlag,
} from "@/features/admin-feature-flags/hooks/use-feature-flags";
import { cn } from "@/lib/utils";

function formatWhen(value: string | null) {
  if (!value) return "—";
  try {
    return new Date(value).toLocaleString();
  } catch {
    return value;
  }
}

export function FeatureFlagsWorkspace() {
  const [search, setSearch] = React.useState("");
  const query = useFeatureFlags(search);
  const patch = usePatchFeatureFlag();
  const items = query.data?.items ?? [];

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">Feature Flags</h1>
          <p className="text-muted-foreground text-xs">
            Operational controls for PlacementOS capabilities. Critical flags
            cannot be disabled.
          </p>
        </div>
        <Input
          className="max-w-xs"
          placeholder="Search flags…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <span className="text-muted-foreground text-xs">
          {query.data ? `${query.data.total} flags` : "Loading…"}
        </span>
      </header>

      <div className="hidden min-h-0 flex-1 overflow-auto md:block">
        <table className="w-full min-w-[960px] border-collapse text-sm">
          <thead className="bg-background sticky top-0 border-b text-left text-xs">
            <tr className="text-muted-foreground">
              <th className="px-4 py-3">Flag</th>
              <th className="px-4 py-3">Description</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Scope</th>
              <th className="px-4 py-3">Updated By</th>
              <th className="px-4 py-3">Updated At</th>
              <th className="px-4 py-3">Toggle</th>
            </tr>
          </thead>
          <tbody>
            {query.isLoading &&
              Array.from({ length: 8 }).map((_, i) => (
                <tr key={i} className="border-b">
                  <td colSpan={7} className="px-4 py-3">
                    <div className="bg-muted h-8 animate-pulse rounded" />
                  </td>
                </tr>
              ))}
            {!query.isLoading && items.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="text-muted-foreground px-4 py-12 text-center"
                >
                  No feature flags found.
                </td>
              </tr>
            )}
            {items.map((flag) => (
              <tr key={flag.key} className="border-b align-top">
                <td className="px-4 py-3">
                  <p className="font-medium">{flag.name}</p>
                  <p className="text-muted-foreground font-mono text-[11px]">
                    {flag.key}
                  </p>
                  {flag.critical && (
                    <span className="mt-1 inline-block rounded bg-amber-500/15 px-1.5 py-0.5 text-[10px] text-amber-900">
                      Critical
                    </span>
                  )}
                </td>
                <td className="text-muted-foreground max-w-sm px-4 py-3 text-xs">
                  {flag.description || "—"}
                </td>
                <td className="px-4 py-3">
                  <span
                    className={cn(
                      "rounded px-2 py-0.5 text-xs capitalize",
                      flag.enabled
                        ? "bg-emerald-500/10 text-emerald-800"
                        : "bg-muted text-muted-foreground",
                    )}
                  >
                    {flag.enabled ? "Enabled" : "Disabled"}
                  </span>
                </td>
                <td className="px-4 py-3 text-xs">{flag.scope}</td>
                <td className="px-4 py-3 text-xs">
                  {flag.updated_by_email || "—"}
                </td>
                <td className="px-4 py-3 text-xs">
                  {formatWhen(flag.updated_at)}
                </td>
                <td className="px-4 py-3">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={
                      patch.isPending || (flag.critical && flag.enabled)
                    }
                    title={
                      flag.critical
                        ? "Critical flags cannot be disabled"
                        : undefined
                    }
                    onClick={async () => {
                      const next = !flag.enabled;
                      const action = next ? "enable" : "disable";
                      if (
                        !window.confirm(
                          `${action === "enable" ? "Enable" : "Disable"} “${flag.name}”?`,
                        )
                      ) {
                        return;
                      }
                      try {
                        await patch.mutateAsync({
                          key: flag.key,
                          enabled: next,
                        });
                        toast.success(
                          `${flag.name} ${next ? "enabled" : "disabled"}`,
                        );
                      } catch (err) {
                        toast.error(
                          err instanceof Error ? err.message : "Update failed",
                        );
                      }
                    }}
                  >
                    {flag.enabled ? "Disable" : "Enable"}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-3 overflow-auto p-4 md:hidden">
        {items.map((flag) => (
          <div key={flag.key} className="rounded-lg border p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium">{flag.name}</p>
                <p className="text-muted-foreground font-mono text-[11px]">
                  {flag.key}
                </p>
              </div>
              <span
                className={cn(
                  "rounded px-2 py-0.5 text-xs",
                  flag.enabled
                    ? "bg-emerald-500/10 text-emerald-800"
                    : "bg-muted",
                )}
              >
                {flag.enabled ? "On" : "Off"}
              </span>
            </div>
            <p className="text-muted-foreground mt-2 text-xs">
              {flag.description}
            </p>
            <p className="text-muted-foreground mt-2 text-[11px]">
              {flag.scope} · {flag.updated_by_email || "system"} ·{" "}
              {formatWhen(flag.updated_at)}
            </p>
            <Button
              type="button"
              size="sm"
              variant="outline"
              className="mt-3"
              disabled={patch.isPending || (flag.critical && flag.enabled)}
              onClick={async () => {
                const next = !flag.enabled;
                if (
                  !window.confirm(
                    `${next ? "Enable" : "Disable"} “${flag.name}”?`,
                  )
                ) {
                  return;
                }
                try {
                  await patch.mutateAsync({ key: flag.key, enabled: next });
                  toast.success("Updated");
                } catch (err) {
                  toast.error(
                    err instanceof Error ? err.message : "Update failed",
                  );
                }
              }}
            >
              {flag.enabled ? "Disable" : "Enable"}
            </Button>
          </div>
        ))}
      </div>
    </div>
  );
}
