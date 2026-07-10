"use client";

import { ExternalLink } from "lucide-react";

import { Button } from "@/components/ui/button";
import { CrmStatusBadge } from "@/features/company-crm/components/crm-status-badge";
import { HandlerBadge } from "@/features/company-crm/components/handler-badge";
import { PipelineBadge } from "@/features/company-crm/components/pipeline-badge";
import type { Company } from "@/features/company-crm/types";
import { formatRelativeDate } from "@/features/company-crm/utils/filter-companies";

type OverviewTabProps = {
  company: Company;
  onEdit: () => void;
  onUpdatePipeline: () => void;
  onAssignHandler: () => void;
};

export function OverviewTab({
  company,
  onEdit,
  onUpdatePipeline,
  onAssignHandler,
}: OverviewTabProps) {
  return (
    <div className="space-y-6 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <CrmStatusBadge status={company.status} />
        {company.pipeline && (
          <PipelineBadge stage={company.pipeline.current_stage} />
        )}
      </div>

      <dl className="grid gap-4 sm:grid-cols-2">
        <InfoItem label="Industry" value={company.industry} />
        <InfoItem label="Company Type" value={company.company_type} />
        <InfoItem label="Headquarters" value={company.headquarters} />
        <InfoItem label="Website" value={company.website} isLink />
        <InfoItem label="LinkedIn" value={company.linkedin} isLink />
        <InfoItem
          label="Created"
          value={formatRelativeDate(company.created_at)}
        />
        <InfoItem
          label="Last Updated"
          value={formatRelativeDate(company.updated_at)}
        />
      </dl>

      <div>
        <h4 className="mb-2 text-sm font-medium">Current Handler</h4>
        {company.active_handler ? (
          <HandlerBadge
            handlerId={company.active_handler.handler_user_id}
            ownershipType={company.active_handler.ownership_type}
            branch={company.active_handler.branch}
          />
        ) : (
          <p className="text-muted-foreground text-sm">No handler assigned</p>
        )}
      </div>

      <div className="flex flex-wrap gap-2 border-t pt-4">
        <Button type="button" size="sm" variant="outline" onClick={onEdit}>
          Edit Company
        </Button>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={onUpdatePipeline}
        >
          Update Pipeline
        </Button>
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={onAssignHandler}
        >
          Assign Handler
        </Button>
      </div>
    </div>
  );
}

function InfoItem({
  label,
  value,
  isLink,
}: {
  label: string;
  value: string | null | undefined;
  isLink?: boolean;
}) {
  return (
    <div>
      <dt className="text-muted-foreground text-xs">{label}</dt>
      <dd className="mt-0.5 text-sm">
        {!value ? (
          "—"
        ) : isLink ? (
          <a
            href={value}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary inline-flex items-center gap-1 hover:underline"
          >
            Open <ExternalLink className="h-3 w-3" />
          </a>
        ) : (
          value
        )}
      </dd>
    </div>
  );
}
