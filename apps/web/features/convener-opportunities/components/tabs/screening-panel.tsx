"use client";

import { Button } from "@/components/ui/button";
import { SummaryCard } from "@/features/convener-opportunities/components/summary-card";
import { OperationsEmptyState } from "@/features/convener-opportunities/components/empty-state";
import { TabPanelSkeleton } from "@/features/convener-opportunities/components/loading-skeleton";
import { useScreeningSummary } from "@/features/eligibility/hooks/use-eligibility-engine";

type ScreeningPanelProps = {
  opportunityId: string;
};

export function ScreeningPanel({ opportunityId }: ScreeningPanelProps) {
  const screeningQuery = useScreeningSummary(opportunityId);

  if (screeningQuery.isLoading) {
    return <TabPanelSkeleton />;
  }

  if (screeningQuery.isError) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Could not load screening summary.</p>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-3"
          onClick={() => screeningQuery.refetch()}
        >
          Retry
        </Button>
      </div>
    );
  }

  const summary = screeningQuery.data;

  if (!summary || summary.total_applications === 0) {
    return (
      <div className="p-6">
        <OperationsEmptyState
          title="No applications to screen"
          description="Screening results will appear once students apply to this opportunity."
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <SummaryCard
          label="Total applications"
          value={summary.total_applications}
        />
        <SummaryCard
          label="Eligible"
          value={summary.eligible_count}
          className="border-emerald-500/20"
        />
        <SummaryCard
          label="Ineligible"
          value={summary.ineligible_count}
          className="border-red-500/20"
        />
      </div>

      <section>
        <h3 className="mb-3 text-sm font-semibold">Reason breakdown</h3>
        {summary.reason_breakdown.length === 0 ? (
          <OperationsEmptyState
            title="No failed rules"
            description="Every applicant currently meets the eligibility criteria."
          />
        ) : (
          <div className="overflow-x-auto rounded-lg border">
            <table className="w-full min-w-[420px] text-left text-sm">
              <thead className="bg-muted/30 text-muted-foreground border-b text-xs">
                <tr>
                  <th className="px-4 py-3 font-medium">Reason</th>
                  <th className="px-4 py-3 font-medium">Code</th>
                  <th className="px-4 py-3 text-right font-medium">
                    Applicants
                  </th>
                </tr>
              </thead>
              <tbody>
                {summary.reason_breakdown.map((item) => (
                  <tr key={item.code} className="border-b last:border-0">
                    <td className="px-4 py-3 font-medium">{item.title}</td>
                    <td className="text-muted-foreground px-4 py-3">
                      {item.code}
                    </td>
                    <td className="px-4 py-3 text-right tabular-nums">
                      {item.count}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
