import type { ReactNode } from "react";

import {
  EMPLOYMENT_LABELS,
  MODE_LABELS,
} from "@/features/student-opportunities/constants";
import type { OpportunityDetail } from "@/features/student-opportunities/types";
import { formatCtc } from "@/features/student-opportunities/utils/filter-opportunities";

type OverviewTabProps = {
  detail: OpportunityDetail;
};

function Field({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="rounded-lg border p-3">
      <dt className="text-muted-foreground text-xs font-medium">{label}</dt>
      <dd className="mt-1 text-sm">{value}</dd>
    </div>
  );
}

export function OverviewTab({ detail }: OverviewTabProps) {
  const deadline = new Date(detail.application_deadline).toLocaleString(
    undefined,
    {
      dateStyle: "medium",
      timeStyle: "short",
    },
  );

  return (
    <dl className="grid gap-3 p-4 sm:grid-cols-2">
      <Field label="Role" value={detail.role} />
      <Field label="Posting" value={detail.title} />
      <Field label="Location" value={detail.location} />
      <Field label="Mode" value={MODE_LABELS[detail.mode]} />
      <Field
        label="Employment"
        value={EMPLOYMENT_LABELS[detail.employment_type]}
      />
      <Field label="CTC" value={formatCtc(detail.ctc_min, detail.ctc_max)} />
      <Field label="Bond" value={detail.bond_details ?? "None specified"} />
      <Field label="Deadline" value={deadline} />
      <div className="rounded-lg border p-3 sm:col-span-2">
        <dt className="text-muted-foreground text-xs font-medium">
          Description
        </dt>
        <dd className="mt-2 text-sm whitespace-pre-wrap">
          {detail.job_description}
        </dd>
      </div>
    </dl>
  );
}
