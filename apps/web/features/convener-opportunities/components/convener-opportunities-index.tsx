"use client";

import Link from "next/link";
import { useMemo } from "react";

import { Button } from "@/components/ui/button";
import { DeadlineBadge } from "@/features/student-opportunities/components/deadline-badge";
import { OpportunityStatusBadge } from "@/features/convener-opportunities/components/status-badge";
import { OperationsEmptyState } from "@/features/convener-opportunities/components/empty-state";
import { OpportunityListSkeleton } from "@/features/student-opportunities/components/loading-skeleton";
import { fetchOpportunities } from "@/features/student-opportunities/api/opportunity-client";
import { fetchCompanies } from "@/features/company-crm/api/company-client";
import { useQuery } from "@tanstack/react-query";

export function ConvenerOpportunitiesIndex() {
  const opportunitiesQuery = useQuery({
    queryKey: ["convener-opportunities", "list"],
    queryFn: fetchOpportunities,
    staleTime: 60_000,
  });

  const companiesQuery = useQuery({
    queryKey: ["companies", "list"],
    queryFn: () => fetchCompanies(),
    staleTime: 5 * 60_000,
  });

  const companyMap = useMemo(() => {
    const map = new Map<string, string>();
    for (const company of companiesQuery.data ?? []) {
      map.set(company.id, company.name);
    }
    return map;
  }, [companiesQuery.data]);

  const isLoading = opportunitiesQuery.isLoading || companiesQuery.isLoading;

  if (isLoading) {
    return (
      <div className="-m-6 p-6">
        <h1 className="text-xl font-semibold">Opportunity Operations</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Select a published opportunity to manage applications.
        </p>
        <div className="mt-6">
          <OpportunityListSkeleton />
        </div>
      </div>
    );
  }

  if (opportunitiesQuery.isError) {
    return (
      <div className="-m-6 p-6 text-center">
        <p className="text-destructive">Could not load opportunities.</p>
        <Button
          type="button"
          variant="outline"
          className="mt-4"
          onClick={() => opportunitiesQuery.refetch()}
        >
          Retry
        </Button>
      </div>
    );
  }

  const items = opportunitiesQuery.data ?? [];

  return (
    <div className="-m-6 p-6">
      <h1 className="text-xl font-semibold">Opportunity Operations</h1>
      <p className="text-muted-foreground mt-1 text-sm">
        Select an opportunity to manage applications and track hiring progress.
      </p>

      {items.length === 0 ? (
        <div className="mt-6">
          <OperationsEmptyState
            title="No opportunities found"
            description="Create and publish hiring opportunities to manage applications here."
          />
        </div>
      ) : (
        <div className="mt-6 space-y-2">
          {items.map((item) => (
            <Link
              key={item.id}
              href={`/workspace/convener/opportunities/${item.id}`}
              className="hover:border-primary/40 hover:bg-accent/50 flex items-start justify-between gap-4 rounded-lg border p-4 transition-colors"
            >
              <div className="min-w-0">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium">{item.title}</p>
                  <OpportunityStatusBadge status={item.status} />
                </div>
                <p className="text-muted-foreground mt-1 text-sm">
                  {companyMap.get(item.company_id) ?? "Unknown company"} ·{" "}
                  {item.role}
                </p>
              </div>
              <DeadlineBadge deadline={item.application_deadline} />
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
