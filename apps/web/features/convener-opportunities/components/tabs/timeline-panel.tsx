import { Button } from "@/components/ui/button";
import {
  TIMELINE_STAGE_LABELS,
  TIMELINE_STAGES_ORDER,
} from "@/features/convener-opportunities/constants";
import type { TimelineEntry } from "@/features/convener-opportunities/types";
import type { TimelineStage } from "@/features/student-opportunities/types";
import { cn } from "@/lib/utils";

type TimelinePanelProps = {
  timeline: TimelineEntry[] | undefined;
  currentStage: TimelineStage | null;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
};

export function TimelinePanel({
  timeline,
  currentStage,
  isLoading,
  isError,
  onRetry,
}: TimelinePanelProps) {
  if (isLoading) {
    return (
      <p className="text-muted-foreground p-6 text-sm">Loading timeline...</p>
    );
  }

  if (isError) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Could not load timeline.</p>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-3"
          onClick={onRetry}
        >
          Retry
        </Button>
      </div>
    );
  }

  const reachedStages = new Set(timeline?.map((entry) => entry.stage) ?? []);
  if (currentStage) reachedStages.add(currentStage);

  return (
    <div className="p-6">
      <ol className="relative space-y-0 border-l pl-6">
        {TIMELINE_STAGES_ORDER.map((stage, index) => {
          const reached = reachedStages.has(stage);
          const entry = timeline?.find((item) => item.stage === stage);

          return (
            <li key={stage} className="relative pb-8 last:pb-0">
              <span
                className={cn(
                  "bg-background absolute top-1 -left-[9px] h-4 w-4 rounded-full border-2",
                  reached
                    ? "border-primary bg-primary"
                    : "border-muted-foreground/30",
                )}
                aria-hidden="true"
              />
              <div
                className={cn(
                  reached ? "text-foreground" : "text-muted-foreground",
                )}
              >
                <p className="text-sm font-medium">
                  {index + 1}. {TIMELINE_STAGE_LABELS[stage]}
                </p>
                {entry && (
                  <p className="text-muted-foreground mt-1 text-xs">
                    {new Date(entry.created_at).toLocaleString()}
                    {entry.remarks ? ` · ${entry.remarks}` : ""}
                  </p>
                )}
              </div>
            </li>
          );
        })}
      </ol>
    </div>
  );
}
