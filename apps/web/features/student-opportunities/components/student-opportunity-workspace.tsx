"use client";

import * as React from "react";
import { useMemo } from "react";

import { FilterSidebar } from "@/features/student-opportunities/components/filter-sidebar";
import { OpportunityDetailPanel } from "@/features/student-opportunities/components/opportunity-detail-panel";
import { OpportunityList } from "@/features/student-opportunities/components/opportunity-list";
import { PortalHeader } from "@/features/student-opportunities/components/portal-header";
import { useMyApplications } from "@/features/student-opportunities/hooks/use-applications";
import { useOpportunityFilters } from "@/features/student-opportunities/hooks/use-opportunity-filters";
import {
  useOpportunitiesList,
  useOpportunityDetailsBatch,
  usePrefetchOpportunity,
} from "@/features/student-opportunities/hooks/use-opportunities";
import { useStudentEligibilityBatch } from "@/features/eligibility/hooks/use-eligibility-engine";
import type {
  EligibilityCheck,
  OpportunityTab,
} from "@/features/student-opportunities/types";
import {
  buildApplicationMap,
  enrichOpportunities,
  extractLocations,
  filterOpportunities,
} from "@/features/student-opportunities/utils/filter-opportunities";
import { useStudentProfile } from "@/features/student-onboarding/hooks/use-student-data";

export function StudentOpportunityWorkspace() {
  const [selectedId, setSelectedId] = React.useState<string | null>(null);
  const [activeTab, setActiveTab] = React.useState<OpportunityTab>("overview");

  const { filters, setFilter, resetFilters, hasActiveFilters } =
    useOpportunityFilters();
  const prefetch = usePrefetchOpportunity();

  const listQuery = useOpportunitiesList();
  const applicationsQuery = useMyApplications();

  const listIds = useMemo(
    () => (listQuery.data ?? []).map((item) => item.id),
    [listQuery.data],
  );

  const detailQueries = useOpportunityDetailsBatch(listIds);

  const detailsMap = useMemo(() => {
    const map = new Map<
      string,
      NonNullable<(typeof detailQueries)[number]["data"]>
    >();
    listIds.forEach((id, index) => {
      const data = detailQueries[index]?.data;
      if (data) map.set(id, data);
    });
    return map;
  }, [listIds, detailQueries]);

  const applicationMap = useMemo(
    () => buildApplicationMap(applicationsQuery.data ?? []),
    [applicationsQuery.data],
  );

  const enriched = useMemo(
    () => enrichOpportunities(listQuery.data ?? [], detailsMap, applicationMap),
    [listQuery.data, detailsMap, applicationMap],
  );

  const filtered = useMemo(
    () => filterOpportunities(enriched, filters),
    [enriched, filters],
  );

  const locations = useMemo(
    () => extractLocations(listQuery.data ?? []),
    [listQuery.data],
  );

  const filteredIds = useMemo(
    () => filtered.map((item) => item.list.id),
    [filtered],
  );

  const profileQuery = useStudentProfile();
  const profileId = profileQuery.data?.id;

  const evaluationQueries = useStudentEligibilityBatch(
    filteredIds,
    profileId,
    Boolean(profileId),
  );

  const eligibilityMap = useMemo(() => {
    const map = new Map<string, EligibilityCheck>();
    filteredIds.forEach((id, index) => {
      const evaluation = evaluationQueries[index]?.data;
      if (!evaluation) return;
      map.set(id, {
        eligible: evaluation.eligible,
        reasons: evaluation.reasons.map((reason) => reason.title),
      });
    });
    return map;
  }, [filteredIds, evaluationQueries]);

  const selectedApplication = selectedId
    ? applicationMap.get(selectedId)
    : undefined;

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setActiveTab("overview");
    prefetch(id);
  };

  const handleRefresh = () => {
    void listQuery.refetch();
    void applicationsQuery.refetch();
  };

  const isRefreshing = listQuery.isFetching || applicationsQuery.isFetching;

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <PortalHeader onRefresh={handleRefresh} isRefreshing={isRefreshing} />

      <div className="flex flex-1 overflow-hidden">
        <div className="hidden w-64 shrink-0 lg:block">
          <FilterSidebar
            filters={filters}
            onFilterChange={setFilter}
            onReset={resetFilters}
            locations={locations}
            hasActiveFilters={hasActiveFilters}
          />
        </div>

        <div className="flex w-full min-w-0 flex-1 overflow-hidden">
          <section
            className="w-full shrink-0 overflow-hidden border-r md:w-80 lg:w-96"
            aria-label="Opportunity list panel"
          >
            <OpportunityList
              items={filtered}
              selectedId={selectedId}
              onSelect={handleSelect}
              isLoading={listQuery.isLoading}
              isError={listQuery.isError}
              onRetry={() => listQuery.refetch()}
              eligibilityMap={eligibilityMap}
            />
          </section>

          <section
            className="hidden min-w-0 flex-1 md:block"
            aria-label="Opportunity detail panel"
          >
            <OpportunityDetailPanel
              opportunityId={selectedId}
              activeTab={activeTab}
              onTabChange={setActiveTab}
              application={selectedApplication}
            />
          </section>

          {selectedId && (
            <section
              className="bg-background fixed inset-0 z-40 md:hidden"
              aria-label="Opportunity detail panel mobile"
            >
              <div className="flex h-full flex-col">
                <button
                  type="button"
                  onClick={() => setSelectedId(null)}
                  className="text-primary border-b px-4 py-3 text-left text-sm"
                >
                  ← Back to list
                </button>
                <div className="flex-1 overflow-hidden">
                  <OpportunityDetailPanel
                    opportunityId={selectedId}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                    application={selectedApplication}
                  />
                </div>
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
