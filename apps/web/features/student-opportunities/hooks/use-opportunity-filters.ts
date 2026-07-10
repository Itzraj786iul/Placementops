"use client";

import * as React from "react";

import { DEFAULT_FILTERS } from "@/features/student-opportunities/constants";
import type { OpportunityFilters } from "@/features/student-opportunities/types";

export function useOpportunityFilters() {
  const [filters, setFilters] = React.useState<OpportunityFilters>({
    ...DEFAULT_FILTERS,
  });

  const setFilter = React.useCallback(
    <K extends keyof OpportunityFilters>(
      key: K,
      value: OpportunityFilters[K],
    ) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
    },
    [],
  );

  const resetFilters = React.useCallback(() => {
    setFilters({ ...DEFAULT_FILTERS });
  }, []);

  const hasActiveFilters = React.useMemo(
    () =>
      filters.search.trim() !== "" ||
      filters.employmentType != null ||
      filters.location != null ||
      filters.mode != null ||
      filters.ctcMin != null ||
      filters.ctcMax != null ||
      filters.departmentId != null ||
      filters.applicationStatus != null,
    [filters],
  );

  return { filters, setFilter, resetFilters, hasActiveFilters };
}
