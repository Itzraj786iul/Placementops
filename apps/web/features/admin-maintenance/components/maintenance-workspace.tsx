"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  useAdminMaintenance,
  usePatchMaintenance,
} from "@/features/admin-maintenance/hooks/use-admin-maintenance";
import { cn } from "@/lib/utils";

const ROLE_OPTIONS = [
  "PLACEMENT_CELL",
  "PLACEMENT_CONVENER",
  "STUDENT",
] as const;

export function MaintenanceWorkspace() {
  const query = useAdminMaintenance();
  const patch = usePatchMaintenance();
  const data = query.data;

  const [enabled, setEnabled] = React.useState(false);
  const [title, setTitle] = React.useState("");
  const [message, setMessage] = React.useState("");
  const [eta, setEta] = React.useState("");
  const [support, setSupport] = React.useState("");
  const [startsAt, setStartsAt] = React.useState("");
  const [endsAt, setEndsAt] = React.useState("");
  const [allowedRoles, setAllowedRoles] = React.useState<string[]>([]);
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => {
    if (!data) return;
    setEnabled(data.enabled);
    setTitle(data.title);
    setMessage(data.message);
    setEta(data.estimated_completion ?? "");
    setSupport(data.support_contact ?? "");
    setStartsAt(data.starts_at ?? "");
    setEndsAt(data.ends_at ?? "");
    setAllowedRoles(data.allowed_roles ?? []);
    setHydrated(true);
  }, [data]);

  const toggleRole = (role: string) => {
    setAllowedRoles((prev) =>
      prev.includes(role) ? prev.filter((r) => r !== role) : [...prev, role],
    );
  };

  const save = async (nextEnabled?: boolean) => {
    const enabling = nextEnabled ?? enabled;
    const label = enabling ? "enable" : "disable";
    if (
      !window.confirm(
        `Confirm ${label} maintenance mode? This affects student and convener write access.`,
      )
    ) {
      return;
    }
    try {
      const result = await patch.mutateAsync({
        enabled: enabling,
        title: title.trim(),
        message: message.trim(),
        estimated_completion: eta.trim() || null,
        support_contact: support.trim() || null,
        starts_at: startsAt.trim() || null,
        ends_at: endsAt.trim() || null,
        allowed_roles: allowedRoles,
        confirm: true,
      });
      setEnabled(result.enabled);
      toast.success(
        result.enabled ? "Maintenance enabled" : "Maintenance disabled",
      );
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (query.isLoading || !hydrated) {
    return (
      <div className="-m-6 space-y-4 p-6">
        <div className="bg-muted h-10 max-w-sm animate-pulse rounded" />
        <div className="bg-muted h-64 animate-pulse rounded-lg" />
      </div>
    );
  }

  return (
    <div className="-m-6 flex flex-col">
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">Maintenance Mode</h1>
          <p className="text-muted-foreground text-xs">
            Temporarily restrict writes and student login. SUPER_ADMIN always
            bypasses.
          </p>
        </div>
        <span
          className={cn(
            "rounded-full px-3 py-1 text-xs font-medium",
            enabled
              ? "bg-amber-500/15 text-amber-900"
              : "bg-emerald-500/10 text-emerald-800",
          )}
        >
          {enabled ? "Enabled" : "Disabled"}
        </span>
      </header>

      <div className="mx-auto grid w-full max-w-5xl gap-6 p-4 md:grid-cols-2 md:p-6">
        <form
          className="space-y-4"
          onSubmit={(e) => {
            e.preventDefault();
            void save(enabled);
          }}
        >
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={enabled}
              onChange={(e) => setEnabled(e.target.checked)}
            />
            Maintenance mode enabled
          </label>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Title</label>
            <Input value={title} onChange={(e) => setTitle(e.target.value)} />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Message</label>
            <Textarea
              rows={5}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Estimated completion</label>
            <Input
              placeholder="e.g. 11 Jul 2026, 6:00 PM IST"
              value={eta}
              onChange={(e) => setEta(e.target.value)}
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-medium">Support contact</label>
            <Input
              placeholder="placement@nitrr.ac.in"
              value={support}
              onChange={(e) => setSupport(e.target.value)}
            />
          </div>

          <div className="grid gap-3 md:grid-cols-2">
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Starts at</label>
              <Input
                type="datetime-local"
                value={startsAt}
                onChange={(e) => setStartsAt(e.target.value)}
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-sm font-medium">Ends at</label>
              <Input
                type="datetime-local"
                value={endsAt}
                onChange={(e) => setEndsAt(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <p className="text-sm font-medium">Allowed roles (write / login)</p>
            <p className="text-muted-foreground text-xs">
              SUPER_ADMIN always bypasses. Conveners are read-only unless
              listed.
            </p>
            <div className="flex flex-wrap gap-2">
              {ROLE_OPTIONS.map((role) => (
                <label
                  key={role}
                  className={cn(
                    "cursor-pointer rounded border px-2 py-1 text-xs",
                    allowedRoles.includes(role) && "bg-muted",
                  )}
                >
                  <input
                    type="checkbox"
                    className="mr-1"
                    checked={allowedRoles.includes(role)}
                    onChange={() => toggleRole(role)}
                  />
                  {role}
                </label>
              ))}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={patch.isPending}>
              Save configuration
            </Button>
            <Button
              type="button"
              variant="outline"
              disabled={patch.isPending}
              onClick={() => void save(!enabled)}
            >
              {enabled ? "Disable now" : "Enable now"}
            </Button>
            <Button type="button" variant="ghost" asChild>
              <a href="/maintenance" target="_blank" rel="noreferrer">
                Open public screen
              </a>
            </Button>
          </div>
        </form>

        <section className="rounded-lg border p-5">
          <p className="text-muted-foreground mb-3 text-xs tracking-wide uppercase">
            Preview
          </p>
          <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-6">
            <p className="text-xs font-medium tracking-wide text-amber-900 uppercase">
              Maintenance
            </p>
            <h2 className="mt-2 text-xl font-semibold">{title || "Title"}</h2>
            <p className="text-muted-foreground mt-3 text-sm whitespace-pre-wrap">
              {message || "Message"}
            </p>
            {eta && (
              <p className="mt-4 text-sm">
                <span className="text-muted-foreground">ETA: </span>
                {eta}
              </p>
            )}
            {support && (
              <p className="mt-1 text-sm">
                <span className="text-muted-foreground">Support: </span>
                {support}
              </p>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
