import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { isDeadlinePassed } from "@/features/student-opportunities/utils/filter-opportunities";

type DeadlineBadgeProps = {
  deadline: string;
  className?: string;
};

export function DeadlineBadge({ deadline, className }: DeadlineBadgeProps) {
  const passed = isDeadlinePassed(deadline);
  const date = new Date(deadline).toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });

  return (
    <Badge
      variant="secondary"
      className={cn(
        passed
          ? "bg-red-500/10 text-red-700 dark:text-red-300"
          : "bg-muted text-muted-foreground",
        className,
      )}
      aria-label={passed ? `Deadline passed: ${date}` : `Deadline: ${date}`}
    >
      {passed ? "Closed" : `Due ${date}`}
    </Badge>
  );
}
