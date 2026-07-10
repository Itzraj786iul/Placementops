"use client";

import * as React from "react";

import { DEFAULT_APPLICATION_FILTERS } from "@/features/convener-opportunities/constants";
import type {
  ApplicationFilters,
  ApplicationSortField,
  SortDirection,
} from "@/features/convener-opportunities/types";

export function useApplicationFilters() {
  const [filters, setFilters] = React.useState<ApplicationFilters>({
    ...DEFAULT_APPLICATION_FILTERS,
  });
  const [sortField, setSortField] =
    React.useState<ApplicationSortField>("applied_at");
  const [sortDirection, setSortDirection] =
    React.useState<SortDirection>("desc");
  const [page, setPage] = React.useState(1);

  const setFilter = React.useCallback(
    <K extends keyof ApplicationFilters>(
      key: K,
      value: ApplicationFilters[K],
    ) => {
      setFilters((prev) => ({ ...prev, [key]: value }));
      setPage(1);
    },
    [],
  );

  const resetFilters = React.useCallback(() => {
    setFilters({ ...DEFAULT_APPLICATION_FILTERS });
    setPage(1);
  }, []);

  const toggleSort = React.useCallback((field: ApplicationSortField) => {
    setSortField((current) => {
      if (current === field) {
        setSortDirection((dir) => (dir === "asc" ? "desc" : "asc"));
        return current;
      }
      setSortDirection("asc");
      return field;
    });
    setPage(1);
  }, []);

  const hasActiveFilters = React.useMemo(
    () =>
      filters.search.trim() !== "" ||
      filters.status != null ||
      filters.department != null ||
      filters.branch != null,
    [filters],
  );

  return {
    filters,
    sortField,
    sortDirection,
    page,
    setPage,
    setFilter,
    resetFilters,
    toggleSort,
    hasActiveFilters,
  };
}
