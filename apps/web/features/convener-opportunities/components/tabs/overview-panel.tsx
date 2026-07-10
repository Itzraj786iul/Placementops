import type { ReactNode } from "react";

import {
  EMPLOYMENT_LABELS,
  MODE_LABELS,
} from "@/features/student-opportunities/constants";
import { formatCtc } from "@/features/student-opportunities/utils/filter-opportunities";
import type { EligibilityRule } from "@/features/student-opportunities/types";
import type { OpportunityWithCompany } from "@/features/convener-opportunities/types";
import type { TimelineEntry } from "@/features/convener-opportunities/types";
import { TIMELINE_STAGE_LABELS } from "@/features/convener-opportunities/constants";

type OverviewPanelProps = {
  opportunity: OpportunityWithCompany;
  eligibility: EligibilityRule | undefined;
  timeline: TimelineEntry[] | undefined;
  isLoadingEligibility: boolean;
  isLoadingTimeline: boolean;
};

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border p-3">
      <dt className="text-muted-foreground text-xs font-medium">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  );
}

export function OverviewPanel({
  opportunity,
  eligibility,
  timeline,
  isLoadingEligibility,
  isLoadingTimeline,
}: OverviewPanelProps) {
  const recent = timeline?.slice(0, 5) ?? [];

  return (
    <div className="space-y-6 p-6">
      <section>
        <h3 className="mb-3 text-sm font-semibold">Opportunity details</h3>
        <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <Field label="Role" value={opportunity.role} />
          <Field label="Company" value={opportunity.companyName} />
          <Field label="Location" value={opportunity.location} />
          <Field label="Mode" value={MODE_LABELS[opportunity.mode]} />
          <Field
            label="Employment"
            value={EMPLOYMENT_LABELS[opportunity.employment_type]}
          />
          <Field
            label="CTC"
            value={formatCtc(opportunity.ctc_min, opportunity.ctc_max)}
          />
          <Field
            label="Bond"
            value={opportunity.bond_details ?? "None specified"}
          />
          <Field
            label="Deadline"
            value={new Date(opportunity.application_deadline).toLocaleString()}
          />
        </dl>
        <div className="mt-3 rounded-lg border p-3">
          <dt className="text-muted-foreground text-xs font-medium">
            Description
          </dt>
          <dd className="mt-2 text-sm whitespace-pre-wrap">
            {opportunity.job_description}
          </dd>
        </div>
      </section>

      <section>
        <h3 className="mb-3 text-sm font-semibold">Eligibility rules</h3>
        {isLoadingEligibility ? (
          <p className="text-muted-foreground text-sm">
            Loading eligibility...
          </p>
        ) : eligibility ? (
          <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <Field
              label="Minimum CGPA"
              value={eligibility.minimum_cgpa ?? "Not specified"}
            />
            <Field
              label="Graduation years"
              value={
                eligibility.allowed_graduation_years?.length
                  ? eligibility.allowed_graduation_years.join(", ")
                  : "All years"
              }
            />
            <Field
              label="Max active backlogs"
              value={eligibility.maximum_active_backlogs ?? "Not specified"}
            />
            <Field
              label="Gender restriction"
              value={eligibility.gender_restriction ?? "None"}
            />
          </dl>
        ) : (
          <p className="text-muted-foreground text-sm">
            No eligibility rules configured.
          </p>
        )}
      </section>

      <section>
        <h3 className="mb-3 text-sm font-semibold">Recent activity</h3>
        {isLoadingTimeline ? (
          <p className="text-muted-foreground text-sm">Loading timeline...</p>
        ) : recent.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            No timeline activity yet.
          </p>
        ) : (
          <ul className="space-y-2">
            {recent.map((entry) => (
              <li
                key={entry.id}
                className="rounded-lg border px-4 py-3 text-sm"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">
                    {TIMELINE_STAGE_LABELS[entry.stage]}
                  </span>
                  <span className="text-muted-foreground text-xs">
                    {new Date(entry.created_at).toLocaleString()}
                  </span>
                </div>
                {entry.remarks && (
                  <p className="text-muted-foreground mt-1">{entry.remarks}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
