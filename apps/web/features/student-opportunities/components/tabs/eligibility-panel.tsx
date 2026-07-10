"use client";

import type { ReactNode } from "react";

import { Button } from "@/components/ui/button";
import { EligibilityEmptyState } from "@/features/eligibility/components/eligibility-empty-state";
import { EligibilityReasonsTable } from "@/features/eligibility/components/eligibility-reasons-table";
import { EligibilityResultBanner } from "@/features/eligibility/components/eligibility-result-banner";
import type { EligibilityEvaluation } from "@/features/eligibility/types";
import type { Department } from "@/features/student-onboarding/types";
import type { EligibilityRule } from "@/features/student-opportunities/types";

type EligibilityPanelProps = {
  rule: EligibilityRule | undefined;
  evaluation: EligibilityEvaluation | undefined;
  departments: Department[];
  isLoadingRules: boolean;
  isLoadingEvaluation: boolean;
  isError: boolean;
  onRetry: () => void;
  profileMissing?: boolean;
};

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border p-3">
      <dt className="text-muted-foreground text-xs font-medium">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  );
}

function formatDepartments(
  rule: EligibilityRule,
  departments: Department[],
): string {
  if (!rule.allowed_departments?.length) return "All departments";
  return rule.allowed_departments
    .map((id) => departments.find((d) => d.id === id)?.name ?? id)
    .join(", ");
}

export function EligibilityPanel({
  rule,
  evaluation,
  departments,
  isLoadingRules,
  isLoadingEvaluation,
  isError,
  onRetry,
  profileMissing = false,
}: EligibilityPanelProps) {
  if (isLoadingRules || isLoadingEvaluation) {
    return (
      <p className="text-muted-foreground p-4 text-sm">
        Checking eligibility...
      </p>
    );
  }

  if (isError) {
    return (
      <div className="p-4 text-center text-sm">
        <p className="text-destructive">
          Could not load eligibility evaluation.
        </p>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-3"
          onClick={onRetry}
        >
          Retry
        </Button>
      </div>
    );
  }

  if (profileMissing) {
    return (
      <div className="p-4">
        <EligibilityEmptyState
          title="Complete your profile"
          description="A student profile is required before eligibility can be evaluated."
        />
      </div>
    );
  }

  if (!rule) {
    return (
      <div className="p-4">
        <EligibilityEmptyState
          title="No eligibility rules"
          description="No eligibility rules are configured for this opportunity. All students are considered eligible."
        />
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      {evaluation && (
        <>
          <EligibilityResultBanner
            eligible={evaluation.eligible}
            eligibleLabel="Eligible — you meet the criteria for this opportunity."
            ineligibleLabel="Not Eligible — one or more rules failed."
          />
          {!evaluation.eligible && (
            <div>
              <h3 className="mb-2 text-sm font-semibold">Failed rules</h3>
              <EligibilityReasonsTable reasons={evaluation.reasons} />
            </div>
          )}
        </>
      )}

      <div>
        <h3 className="mb-2 text-sm font-semibold">Configured rules</h3>
        <dl className="grid gap-3 sm:grid-cols-2">
          <Field
            label="Minimum CGPA"
            value={rule.minimum_cgpa ?? "Not specified"}
          />
          <Field
            label="Departments"
            value={formatDepartments(rule, departments)}
          />
          <Field
            label="Graduation Year"
            value={
              rule.allowed_graduation_years?.length
                ? rule.allowed_graduation_years.join(", ")
                : "All years"
            }
          />
          <Field
            label="Maximum Active Backlogs"
            value={
              rule.maximum_active_backlogs != null
                ? String(rule.maximum_active_backlogs)
                : "Not specified"
            }
          />
          <Field
            label="Gender Restriction"
            value={rule.gender_restriction ?? "None"}
          />
          <Field
            label="Backlog History"
            value={rule.allow_backlog_history ? "Allowed" : "Not allowed"}
          />
        </dl>
      </div>
    </div>
  );
}
