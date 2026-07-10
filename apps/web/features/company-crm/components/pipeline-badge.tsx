import { Badge } from "@/components/ui/badge";
import { PIPELINE_LABELS } from "@/features/company-crm/constants";
import type { PipelineStage } from "@/features/company-crm/types";
import { cn } from "@/lib/utils";

const STAGE_STYLES: Partial<Record<PipelineStage, string>> = {
  INTERESTED:
    "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300",
  DRIVE_PLANNED:
    "bg-blue-100 text-blue-800 dark:bg-blue-950 dark:text-blue-300",
  REJECTED: "bg-red-100 text-red-800 dark:bg-red-950 dark:text-red-300",
  ON_HOLD: "bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300",
};

type PipelineBadgeProps = {
  stage: PipelineStage;
  className?: string;
};

export function PipelineBadge({ stage, className }: PipelineBadgeProps) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "border-transparent font-medium",
        STAGE_STYLES[stage] ?? "bg-muted text-muted-foreground",
        className,
      )}
    >
      {PIPELINE_LABELS[stage]}
    </Badge>
  );
}
