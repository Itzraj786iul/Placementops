"use client";

import { useMemo } from "react";

import { ApplicationTable } from "@/features/convener-opportunities/components/application-table";
import { APPLICATIONS_PAGE_SIZE } from "@/features/convener-opportunities/constants";
import { useApplicationFilters } from "@/features/convener-opportunities/hooks/use-application-filters";
import type { EnrichedApplication } from "@/features/convener-opportunities/types";
import {
  extractBranches,
  extractDepartments,
  filterApplications,
  paginateApplications,
  sortApplications,
} from "@/features/convener-opportunities/utils/application-utils";

type ApplicationsPanelProps = {
  enrichedItems: EnrichedApplication[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onSelectApplication: (applicationId: string) => void;
};

export function ApplicationsPanel({
  enrichedItems,
  isLoading,
  isError,
  onRetry,
  onSelectApplication,
}: ApplicationsPanelProps) {
  const {
    filters,
    sortField,
    sortDirection,
    page,
    setPage,
    setFilter,
    resetFilters,
    toggleSort,
    hasActiveFilters,
  } = useApplicationFilters();

  const filtered = useMemo(
    () =>
      sortApplications(
        filterApplications(enrichedItems, filters),
        sortField,
        sortDirection,
      ),
    [enrichedItems, filters, sortField, sortDirection],
  );

  const pageItems = useMemo(
    () => paginateApplications(filtered, page, APPLICATIONS_PAGE_SIZE),
    [filtered, page],
  );

  const departments = useMemo(
    () => extractDepartments(enrichedItems),
    [enrichedItems],
  );
  const branches = useMemo(
    () => extractBranches(enrichedItems),
    [enrichedItems],
  );

  return (
    <ApplicationTable
      items={filtered}
      pageItems={pageItems}
      totalCount={filtered.length}
      page={page}
      filters={filters}
      sortField={sortField}
      sortDirection={sortDirection}
      departments={departments}
      branches={branches}
      isLoading={isLoading}
      isError={isError}
      onRetry={onRetry}
      onFilterChange={setFilter}
      onResetFilters={resetFilters}
      onToggleSort={toggleSort}
      onPageChange={setPage}
      onSelectApplication={onSelectApplication}
      hasActiveFilters={hasActiveFilters}
    />
  );
}
