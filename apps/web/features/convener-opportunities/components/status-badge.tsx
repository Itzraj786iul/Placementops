import { Badge } from "@/components/ui/badge";
import { OPPORTUNITY_STATUS_LABELS } from "@/features/convener-opportunities/constants";
import type { OpportunityDetail } from "@/features/student-opportunities/types";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<OpportunityDetail["status"], string> = {
  DRAFT: "bg-muted text-muted-foreground",
  PUBLISHED: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  ARCHIVED: "bg-amber-500/10 text-amber-700 dark:text-amber-300",
};

type OpportunityStatusBadgeProps = {
  status: OpportunityDetail["status"];
  className?: string;
};

export function OpportunityStatusBadge({
  status,
  className,
}: OpportunityStatusBadgeProps) {
  return (
    <Badge
      variant="secondary"
      className={cn(STATUS_STYLES[status], className)}
      aria-label={`Opportunity status: ${OPPORTUNITY_STATUS_LABELS[status]}`}
    >
      {OPPORTUNITY_STATUS_LABELS[status]}
    </Badge>
  );
}
