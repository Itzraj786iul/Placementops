import { Badge } from "@/components/ui/badge";
import { APPLICATION_STATUS_LABELS } from "@/features/student-opportunities/constants";
import type { ApplicationStatus } from "@/features/student-opportunities/types";
import { cn } from "@/lib/utils";

const STATUS_STYLES: Partial<Record<ApplicationStatus, string>> = {
  APPLIED: "bg-blue-500/10 text-blue-700 dark:text-blue-300",
  UNDER_REVIEW: "bg-amber-500/10 text-amber-700 dark:text-amber-300",
  SHORTLISTED: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  SELECTED: "bg-emerald-600/10 text-emerald-800 dark:text-emerald-200",
  ACCEPTED: "bg-green-600/10 text-green-800 dark:text-green-200",
  REJECTED: "bg-red-500/10 text-red-700 dark:text-red-300",
  WITHDRAWN: "bg-muted text-muted-foreground",
};

type StatusBadgeProps = {
  status: ApplicationStatus;
  className?: string;
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <Badge
      variant="secondary"
      className={cn(STATUS_STYLES[status], className)}
      aria-label={`Application status: ${APPLICATION_STATUS_LABELS[status]}`}
    >
      {APPLICATION_STATUS_LABELS[status]}
    </Badge>
  );
}
