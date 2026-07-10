import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

type CrmStatusBadgeProps = {
  status: string;
  className?: string;
};

const STYLES: Record<string, string> = {
  ACTIVE: "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300",
  INACTIVE: "bg-muted text-muted-foreground",
};

export function CrmStatusBadge({ status, className }: CrmStatusBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "border-transparent font-medium",
        STYLES[status],
        className,
      )}
    >
      {status.replace(/_/g, " ")}
    </Badge>
  );
}
