"use client";

import { Building2 } from "lucide-react";
import { memo } from "react";

import { Badge } from "@/components/ui/badge";
import { DeadlineBadge } from "@/features/student-opportunities/components/deadline-badge";
import { StatusBadge } from "@/features/student-opportunities/components/status-badge";
import { EMPLOYMENT_LABELS } from "@/features/student-opportunities/constants";
import type { EligibilityCheck } from "@/features/student-opportunities/types";
import type { EnrichedOpportunity } from "@/features/student-opportunities/types";
import { formatCtc } from "@/features/student-opportunities/utils/filter-opportunities";
import { cn } from "@/lib/utils";

type OpportunityCardProps = {
  item: EnrichedOpportunity;
  selected: boolean;
  eligibility?: EligibilityCheck;
  onSelect: (id: string) => void;
};

export const OpportunityCard = memo(function OpportunityCard({
  item,
  selected,
  eligibility,
  onSelect,
}: OpportunityCardProps) {
  const { list, detail, application } = item;

  return (
    <button
      type="button"
      onClick={() => onSelect(list.id)}
      className={cn(
        "w-full rounded-lg border p-3 text-left transition-colors",
        "hover:border-primary/40 hover:bg-accent/50",
        "focus-visible:ring-ring focus-visible:ring-2 focus-visible:outline-none",
        selected && "border-primary bg-accent",
      )}
      aria-current={selected ? "true" : undefined}
      aria-label={`${list.title}, ${list.role}`}
    >
      <div className="flex items-start gap-3">
        <div
          className="bg-muted flex h-10 w-10 shrink-0 items-center justify-center rounded-md"
          aria-hidden="true"
        >
          <Building2 className="text-muted-foreground h-5 w-5" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <p className="truncate font-medium">{list.title}</p>
              <p className="text-muted-foreground truncate text-sm">
                {list.role}
              </p>
            </div>
            <DeadlineBadge deadline={list.application_deadline} />
          </div>
          <div className="mt-2 flex flex-wrap gap-1.5">
            <Badge variant="outline">
              {EMPLOYMENT_LABELS[list.employment_type]}
            </Badge>
            <Badge variant="outline">{list.location}</Badge>
            {application && <StatusBadge status={application.status} />}
          </div>
          <div className="text-muted-foreground mt-2 flex flex-wrap items-center gap-2 text-xs">
            <span>{formatCtc(detail?.ctc_min, detail?.ctc_max)}</span>
            {eligibility && (
              <Badge
                variant="secondary"
                className={
                  eligibility.eligible
                    ? "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300"
                    : "bg-amber-500/10 text-amber-700 dark:text-amber-300"
                }
              >
                {eligibility.eligible ? "Eligible" : "Review eligibility"}
              </Badge>
            )}
            {application && <Badge variant="secondary">Applied</Badge>}
          </div>
        </div>
      </div>
    </button>
  );
});
