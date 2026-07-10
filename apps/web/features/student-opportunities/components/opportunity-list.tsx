"use client";

import { Button } from "@/components/ui/button";
import { OpportunityCard } from "@/features/student-opportunities/components/opportunity-card";
import { PortalEmptyState } from "@/features/student-opportunities/components/empty-state";
import { OpportunityListSkeleton } from "@/features/student-opportunities/components/loading-skeleton";
import type { EligibilityCheck } from "@/features/student-opportunities/types";
import type { EnrichedOpportunity } from "@/features/student-opportunities/types";

type OpportunityListProps = {
  items: EnrichedOpportunity[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  eligibilityMap?: Map<string, EligibilityCheck>;
};

export function OpportunityList({
  items,
  selectedId,
  onSelect,
  isLoading,
  isError,
  onRetry,
  eligibilityMap,
}: OpportunityListProps) {
  if (isLoading) return <OpportunityListSkeleton />;

  if (isError) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Could not load opportunities.</p>
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

  if (items.length === 0) {
    return (
      <div className="p-4">
        <PortalEmptyState
          title="No opportunities found"
          description="Try adjusting your filters or check back later for new campus drives."
        />
      </div>
    );
  }

  return (
    <div
      className="h-full overflow-y-auto p-3"
      role="listbox"
      aria-label="Placement opportunities"
    >
      <div className="space-y-2">
        {items.map((item) => (
          <OpportunityCard
            key={item.list.id}
            item={item}
            selected={selectedId === item.list.id}
            eligibility={eligibilityMap?.get(item.list.id)}
            onSelect={onSelect}
          />
        ))}
      </div>
    </div>
  );
}
