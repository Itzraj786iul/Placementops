"use client";

import { memo } from "react";

import { CrmStatusBadge } from "@/features/company-crm/components/crm-status-badge";
import { HandlerBadge } from "@/features/company-crm/components/handler-badge";
import { PipelineBadge } from "@/features/company-crm/components/pipeline-badge";
import type { CompanyListItem } from "@/features/company-crm/types";
import { formatRelativeDate } from "@/features/company-crm/utils/filter-companies";
import { cn } from "@/lib/utils";

type CompanyCardProps = {
  company: CompanyListItem;
  selected: boolean;
  lastCommunication?: string | null;
  onSelect: (id: string) => void;
};

export const CompanyCard = memo(function CompanyCard({
  company,
  selected,
  lastCommunication,
  onSelect,
}: CompanyCardProps) {
  return (
    <button
      type="button"
      onClick={() => onSelect(company.id)}
      className={cn(
        "w-full rounded-lg border p-3 text-left transition-colors",
        "hover:border-primary/40 hover:bg-accent/50",
        "focus-visible:ring-ring focus-visible:ring-2 focus-visible:outline-none",
        selected && "border-primary bg-accent",
      )}
      aria-current={selected ? "true" : undefined}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="truncate font-medium">{company.name}</p>
          <p className="text-muted-foreground truncate text-xs">
            {company.industry ?? "No industry"}
          </p>
        </div>
        <CrmStatusBadge status={company.status} />
      </div>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {company.pipeline && (
          <PipelineBadge stage={company.pipeline.current_stage} />
        )}
      </div>
      <div className="text-muted-foreground mt-2 space-y-1 text-xs">
        {company.active_handler ? (
          <HandlerBadge
            handlerId={company.active_handler.handler_user_id}
            ownershipType={company.active_handler.ownership_type}
            branch={company.active_handler.branch}
          />
        ) : (
          <span>No handler assigned</span>
        )}
        <p>Last comm: {formatRelativeDate(lastCommunication)}</p>
      </div>
    </button>
  );
});
