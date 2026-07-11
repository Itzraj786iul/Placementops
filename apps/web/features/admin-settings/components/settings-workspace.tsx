"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  useAdminSettings,
  usePatchAdminSettings,
} from "@/features/admin-settings/hooks/use-admin-settings";
import { cn } from "@/lib/utils";

const SECTION_LABELS: Record<string, string> = {
  general: "General",
  authentication: "Authentication",
  notifications: "Notifications",
  storage: "Storage",
  placement: "Placement Defaults",
  security: "Security",
};

const FIELD_LABELS: Record<string, string> = {
  "general.college_name": "College Name",
  "general.college_logo_url": "College Logo URL",
  "general.placement_office_email": "Placement Office Email",
  "general.support_email": "Support Email",
  "general.timezone": "Timezone",
  "general.academic_year_format": "Academic Year Format",
  "auth.google_oauth_enabled": "Google OAuth Enabled",
  "auth.allowed_email_domains": "Allowed Email Domains",
  "auth.session_timeout_minutes": "Session Timeout (minutes)",
  "auth.login_message": "Login Message",
  "notifications.default_email_enabled": "Default Email Enabled",
  "notifications.default_in_app_enabled": "Default In-App Enabled",
  "notifications.daily_digest_enabled": "Daily Digest",
  "placement.default_deadline_offset_days":
    "Default Application Deadline Offset (days)",
  "placement.default_resume_required": "Default Resume Requirement",
  "placement.default_eligibility_behaviour": "Default Eligibility Behaviour",
  "placement.auto_close_applications": "Auto Close Applications",
};

function deepEqual(a: unknown, b: unknown) {
  return JSON.stringify(a) === JSON.stringify(b);
}

function StatusPill({ ok, label }: { ok: boolean; label: string }) {
  return (
    <span
      className={cn(
        "rounded px-2 py-0.5 text-xs",
        ok
          ? "bg-emerald-500/10 text-emerald-700"
          : "bg-muted text-muted-foreground",
      )}
    >
      {label}
    </span>
  );
}

export function SettingsWorkspace() {
  const query = useAdminSettings();
  const patch = usePatchAdminSettings();
  const [search, setSearch] = React.useState("");
  const [draft, setDraft] = React.useState<Record<string, unknown>>({});
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => {
    if (query.data && !hydrated) {
      setDraft({ ...query.data.settings });
      setHydrated(true);
    }
  }, [query.data, hydrated]);

  const server = query.data?.settings ?? {};
  const sensitive = new Set(query.data?.sensitive_keys ?? []);
  const dirtyKeys = Object.keys(draft).filter(
    (key) => !deepEqual(draft[key], server[key]),
  );
  const isDirty = dirtyKeys.length > 0;
  const q = search.trim().toLowerCase();

  const matches = (label: string, key?: string) => {
    if (!q) return true;
    return (
      label.toLowerCase().includes(q) ||
      (key ? key.toLowerCase().includes(q) : false)
    );
  };

  const setValue = (key: string, value: unknown) => {
    setDraft((prev) => ({ ...prev, [key]: value }));
  };

  const discard = () => {
    setDraft({ ...server });
  };

  const save = async () => {
    if (!isDirty) return;
    const payload: Record<string, unknown> = {};
    for (const key of dirtyKeys) {
      payload[key] = draft[key];
    }
    const touchesSensitive = dirtyKeys.some((k) => sensitive.has(k));
    if (touchesSensitive) {
      const ok = window.confirm(
        "You are changing sensitive settings (auth / placement behaviour). Continue?",
      );
      if (!ok) return;
    }
    try {
      const result = await patch.mutateAsync({
        settings: payload,
        confirm_sensitive: touchesSensitive,
      });
      setDraft({ ...result.settings });
      toast.success("Settings saved");
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Save failed");
    }
  };

  if (query.isLoading || !hydrated) {
    return (
      <div className="-m-6 space-y-4 p-6">
        <div className="bg-muted h-10 max-w-sm animate-pulse rounded" />
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="bg-muted h-32 animate-pulse rounded-lg" />
        ))}
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="p-6">
        <p className="text-destructive text-sm">
          {query.error instanceof Error
            ? query.error.message
            : "Failed to load settings"}
        </p>
      </div>
    );
  }

  const sections = query.data?.sections ?? {};
  const integrations = query.data?.integrations;

  return (
    <div className={cn("-m-6 flex flex-col", isDirty && "pb-20")}>
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">System Settings</h1>
          <p className="text-muted-foreground text-xs">
            Operational configuration for PlacementOS. Secrets stay in
            environment variables.
          </p>
        </div>
        <Input
          className="max-w-xs"
          placeholder="Search settings…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        {isDirty && (
          <span className="rounded bg-amber-500/15 px-2 py-1 text-xs text-amber-800">
            Unsaved changes ({dirtyKeys.length})
          </span>
        )}
      </header>

      <div className="mx-auto w-full max-w-3xl space-y-8 p-4 md:p-6">
        {Object.entries(sections).map(([sectionId, keys]) => {
          const visibleKeys = keys.filter((key) =>
            matches(FIELD_LABELS[key] ?? key, key),
          );
          if (!visibleKeys.length && q) return null;
          return (
            <section key={sectionId} className="space-y-4">
              <h2 className="text-base font-semibold">
                {SECTION_LABELS[sectionId] ?? sectionId}
              </h2>
              <div className="space-y-4 rounded-lg border p-4">
                {visibleKeys.map((key) => (
                  <SettingField
                    key={key}
                    settingKey={key}
                    value={draft[key]}
                    sensitive={sensitive.has(key)}
                    dirty={!deepEqual(draft[key], server[key])}
                    onChange={(v) => setValue(key, v)}
                  />
                ))}
              </div>
            </section>
          );
        })}

        {integrations && matches(SECTION_LABELS.notifications) && (
          <section className="space-y-4">
            <h2 className="text-base font-semibold">
              Notifications — Templates
            </h2>
            <div className="rounded-lg border p-4">
              <p className="text-muted-foreground mb-2 text-xs">
                Template preview (read-only)
              </p>
              <ul className="grid gap-1 text-sm md:grid-cols-2">
                {integrations.notifications.template_previews.map((name) => (
                  <li key={name} className="font-mono text-xs">
                    {name}
                  </li>
                ))}
              </ul>
              <div className="mt-3 flex flex-wrap gap-2 text-xs">
                <StatusPill
                  ok={integrations.notifications.email_configured}
                  label={
                    integrations.notifications.email_configured
                      ? `Email: ${integrations.notifications.email_provider}`
                      : "Email not configured"
                  }
                />
                <span className="text-muted-foreground">
                  From: {integrations.notifications.email_from}
                </span>
              </div>
            </div>
          </section>
        )}

        {integrations && matches(SECTION_LABELS.storage) && (
          <section className="space-y-4">
            <h2 className="text-base font-semibold">Storage</h2>
            <div className="space-y-3 rounded-lg border p-4 text-sm">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-medium">Cloudinary</span>
                <StatusPill
                  ok={integrations.storage.configured}
                  label={integrations.storage.status}
                />
                {integrations.storage.cloud_name && (
                  <span className="text-muted-foreground text-xs">
                    cloud: {integrations.storage.cloud_name}
                  </span>
                )}
              </div>
              <div>
                <p className="text-muted-foreground mb-1 text-xs">
                  Upload limits (MB)
                </p>
                <p className="text-xs">
                  {Object.entries(integrations.storage.upload_limits_mb)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join(" · ")}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground mb-1 text-xs">
                  Allowed file types
                </p>
                <p className="text-xs">
                  {Object.keys(integrations.storage.allowed_extensions).join(
                    ", ",
                  )}
                </p>
              </div>
              <p className="text-muted-foreground text-xs">
                Integration status is read-only. Secrets are never exposed.
              </p>
            </div>
          </section>
        )}

        {integrations && matches(SECTION_LABELS.security) && (
          <section className="space-y-4">
            <h2 className="text-base font-semibold">Security</h2>
            <div className="grid gap-3 rounded-lg border p-4 text-sm md:grid-cols-2">
              <ReadOnlyRow
                label="Password Policy"
                value={integrations.security.password_policy}
              />
              <ReadOnlyRow
                label="Rate Limit Status"
                value={integrations.security.rate_limit_status}
              />
              <ReadOnlyRow
                label="Audit Logging"
                value={integrations.security.audit_logging_status}
              />
              <ReadOnlyRow
                label="Environment Mode"
                value={integrations.security.environment_mode}
              />
              <ReadOnlyRow
                label="Google OAuth (env)"
                value={
                  integrations.authentication.google_oauth_env_configured
                    ? "Configured"
                    : "Not configured"
                }
              />
              <ReadOnlyRow
                label="Env email domain"
                value={integrations.authentication.env_allowed_email_domain}
              />
            </div>
          </section>
        )}
      </div>

      {isDirty && (
        <div className="bg-background/95 fixed inset-x-0 bottom-0 z-40 border-t px-4 py-3 backdrop-blur">
          <div className="mx-auto flex max-w-3xl items-center justify-between gap-3">
            <p className="text-sm">
              {dirtyKeys.length} unsaved change
              {dirtyKeys.length === 1 ? "" : "s"}
            </p>
            <div className="flex gap-2">
              <Button type="button" variant="outline" onClick={discard}>
                Discard
              </Button>
              <Button
                type="button"
                disabled={patch.isPending}
                onClick={() => void save()}
              >
                {patch.isPending ? "Saving…" : "Save changes"}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ReadOnlyRow({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-muted-foreground text-xs">{label}</p>
      <p className="mt-0.5">{value}</p>
    </div>
  );
}

function SettingField({
  settingKey,
  value,
  sensitive,
  dirty,
  onChange,
}: {
  settingKey: string;
  value: unknown;
  sensitive: boolean;
  dirty: boolean;
  onChange: (value: unknown) => void;
}) {
  const label = FIELD_LABELS[settingKey] ?? settingKey;

  return (
    <div
      className={cn("space-y-1.5", dirty && "rounded-md bg-amber-500/5 p-2")}
    >
      <div className="flex items-center gap-2">
        <label className="text-sm font-medium">{label}</label>
        {sensitive && (
          <span className="text-muted-foreground text-[10px] tracking-wide uppercase">
            Sensitive
          </span>
        )}
      </div>

      {typeof value === "boolean" ? (
        <Select
          value={value ? "true" : "false"}
          onChange={(e) => onChange(e.target.value === "true")}
        >
          <option value="true">Enabled</option>
          <option value="false">Disabled</option>
        </Select>
      ) : settingKey === "auth.allowed_email_domains" ? (
        <Input
          value={Array.isArray(value) ? value.join(", ") : ""}
          onChange={(e) =>
            onChange(
              e.target.value
                .split(",")
                .map((s) => s.trim())
                .filter(Boolean),
            )
          }
          placeholder="nitrr.ac.in, example.edu"
        />
      ) : settingKey === "placement.default_eligibility_behaviour" ? (
        <Select
          value={String(value ?? "strict")}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="strict">Strict</option>
          <option value="advisory">Advisory</option>
          <option value="off">Off</option>
        </Select>
      ) : settingKey === "auth.login_message" ? (
        <Textarea
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
          rows={3}
        />
      ) : typeof value === "number" ||
        settingKey.includes("offset") ||
        settingKey.includes("timeout") ? (
        <Input
          type="number"
          value={Number(value ?? 0)}
          onChange={(e) => onChange(Number(e.target.value))}
        />
      ) : (
        <Input
          value={value == null ? "" : String(value)}
          onChange={(e) =>
            onChange(
              e.target.value === "" && settingKey.includes("logo")
                ? null
                : e.target.value,
            )
          }
        />
      )}
      <p className="text-muted-foreground font-mono text-[10px]">
        {settingKey}
      </p>
    </div>
  );
}
