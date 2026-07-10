"use client";

import { HandlerBadge } from "@/features/company-crm/components/handler-badge";
import { PipelineBadge } from "@/features/company-crm/components/pipeline-badge";
import type { Company } from "@/features/company-crm/types";
import { formatRelativeDate } from "@/features/company-crm/utils/filter-companies";

type HistoryTabProps = {
  company: Company;
};

export function HistoryTab({ company }: HistoryTabProps) {
  return (
    <div className="space-y-6 p-4">
      <section>
        <h4 className="mb-3 text-sm font-medium">Current Handler</h4>
        {company.active_handler ? (
          <div className="space-y-2 rounded-lg border p-4">
            <HandlerBadge
              handlerId={company.active_handler.handler_user_id}
              ownershipType={company.active_handler.ownership_type}
              branch={company.active_handler.branch}
            />
            <p className="text-muted-foreground text-xs">
              Assigned {formatRelativeDate(company.active_handler.assigned_at)}
            </p>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No handler assigned.</p>
        )}
      </section>

      <section>
        <h4 className="mb-3 text-sm font-medium">Current Pipeline Stage</h4>
        {company.pipeline ? (
          <div className="space-y-2 rounded-lg border p-4">
            <PipelineBadge stage={company.pipeline.current_stage} />
            <p className="text-muted-foreground text-xs">
              Last updated {formatRelativeDate(company.pipeline.last_updated)}
            </p>
          </div>
        ) : (
          <p className="text-muted-foreground text-sm">No pipeline data.</p>
        )}
      </section>

      <section className="rounded-md border border-dashed p-4">
        <p className="text-muted-foreground text-sm">
          Full handler assignment history and pipeline change history are not
          available from the current API. Only the active handler and current
          pipeline stage are shown.
        </p>
      </section>
    </div>
  );
}
