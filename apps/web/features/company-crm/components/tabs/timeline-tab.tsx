"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CrmEmptyState } from "@/features/company-crm/components/empty-state";
import { TabContentSkeleton } from "@/features/company-crm/components/loading-skeleton";
import type { TimelineEntry } from "@/features/company-crm/types";
import { formatRelativeDate } from "@/features/company-crm/utils/filter-companies";

type TimelineItemProps = {
  entry: TimelineEntry;
};

export function TimelineItem({ entry }: TimelineItemProps) {
  return (
    <article className="rounded-lg border p-4">
      <div className="flex flex-wrap items-center gap-2">
        <Badge variant="outline">{entry.type.replace(/_/g, " ")}</Badge>
        <time className="text-muted-foreground text-xs">
          {formatRelativeDate(entry.communication_date)}
        </time>
      </div>
      {entry.subject && (
        <h4 className="mt-2 text-sm font-medium">{entry.subject}</h4>
      )}
      <p className="text-muted-foreground mt-1 text-sm whitespace-pre-wrap">
        {entry.description}
      </p>
      <p className="text-muted-foreground mt-2 text-xs">
        Logged by {entry.created_by.slice(0, 8)}…
      </p>
    </article>
  );
}

type TimelineTabProps = {
  timeline: TimelineEntry[] | undefined;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onAddCommunication: () => void;
};

export function TimelineTab({
  timeline,
  isLoading,
  isError,
  onRetry,
  onAddCommunication,
}: TimelineTabProps) {
  if (isLoading) return <TabContentSkeleton />;

  if (isError) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Failed to load timeline.</p>
        <button type="button" onClick={onRetry} className="mt-2 underline">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <div className="flex justify-end">
        <Button type="button" size="sm" onClick={onAddCommunication}>
          Add Communication
        </Button>
      </div>
      {!timeline?.length ? (
        <CrmEmptyState
          title="No communication history yet"
          description="Log calls, emails, and meetings to build a timeline."
          action={
            <Button type="button" size="sm" onClick={onAddCommunication}>
              Add Communication
            </Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {timeline.map((entry) => (
            <TimelineItem key={entry.id} entry={entry} />
          ))}
        </div>
      )}
    </div>
  );
}
