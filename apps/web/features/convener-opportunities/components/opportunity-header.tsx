import { Button } from "@/components/ui/button";
import { DeadlineBadge } from "@/features/student-opportunities/components/deadline-badge";
import { MODE_LABELS } from "@/features/student-opportunities/constants";
import { OpportunityStatusBadge } from "@/features/convener-opportunities/components/status-badge";
import type { OpportunityWithCompany } from "@/features/convener-opportunities/types";

type OpportunityHeaderProps = {
  opportunity: OpportunityWithCompany;
  onRefresh: () => void;
  isRefreshing: boolean;
  onExport: () => void;
  onImport: () => void;
};

export function OpportunityHeader({
  opportunity,
  onRefresh,
  isRefreshing,
  onExport,
  onImport,
}: OpportunityHeaderProps) {
  return (
    <header className="bg-background border-b px-6 py-4">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <h1 className="text-xl font-semibold tracking-tight">
              {opportunity.title}
            </h1>
            <OpportunityStatusBadge status={opportunity.status} />
          </div>
          <p className="text-muted-foreground text-sm">
            {opportunity.companyName} · {opportunity.role}
          </p>
          <div className="flex flex-wrap items-center gap-2">
            <DeadlineBadge deadline={opportunity.application_deadline} />
            <span className="text-muted-foreground text-xs">
              {opportunity.location} · {MODE_LABELS[opportunity.mode]}
            </span>
          </div>
        </div>
        <div className="flex shrink-0 gap-2">
          <Button type="button" variant="outline" size="sm" onClick={onImport}>
            Import
          </Button>
          <Button type="button" variant="outline" size="sm" onClick={onExport}>
            Export
          </Button>
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </Button>
        </div>
      </div>
    </header>
  );
}
