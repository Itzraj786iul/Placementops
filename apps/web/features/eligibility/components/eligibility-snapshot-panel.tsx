import type { ReactNode } from "react";

type EligibilitySnapshotPanelProps = {
  snapshot: Record<string, unknown> | undefined;
};

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border p-3">
      <dt className="text-muted-foreground text-xs font-medium">{label}</dt>
      <dd className="mt-1 text-sm">{value ?? "—"}</dd>
    </div>
  );
}

function displayValue(value: unknown): string {
  if (value == null) return "Not specified";
  if (Array.isArray(value)) {
    return value.length ? value.map(String).join(", ") : "All / unrestricted";
  }
  if (typeof value === "boolean") return value ? "Allowed" : "Not allowed";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function EligibilitySnapshotPanel({
  snapshot,
}: EligibilitySnapshotPanelProps) {
  if (!snapshot || Object.keys(snapshot).length === 0) {
    return (
      <p className="text-muted-foreground text-sm">
        No eligibility rules were snapshotted for this application.
      </p>
    );
  }

  return (
    <dl className="grid gap-3 sm:grid-cols-2">
      <Field label="Minimum CGPA" value={displayValue(snapshot.minimum_cgpa)} />
      <Field
        label="Allowed departments"
        value={displayValue(snapshot.allowed_departments)}
      />
      <Field
        label="Graduation years"
        value={displayValue(snapshot.allowed_graduation_years)}
      />
      <Field
        label="Max active backlogs"
        value={displayValue(snapshot.maximum_active_backlogs)}
      />
      <Field
        label="Backlog history"
        value={displayValue(snapshot.allow_backlog_history)}
      />
      <Field
        label="Gender restriction"
        value={displayValue(snapshot.gender_restriction)}
      />
      {snapshot.education_requirements != null && (
        <div className="rounded-lg border p-3 sm:col-span-2">
          <dt className="text-muted-foreground text-xs font-medium">
            Education requirements
          </dt>
          <dd className="mt-2">
            <pre className="overflow-x-auto text-xs">
              {JSON.stringify(snapshot.education_requirements, null, 2)}
            </pre>
          </dd>
        </div>
      )}
    </dl>
  );
}
