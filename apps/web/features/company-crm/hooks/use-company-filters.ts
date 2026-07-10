"use client";

import * as React from "react";

import type { CompanyFilters } from "@/features/company-crm/types";
import { DEFAULT_FILTERS } from "@/features/company-crm/constants";

export function useCompanyFilters() {
  const [filters, setFilters] = React.useState<CompanyFilters>(DEFAULT_FILTERS);
  const [debouncedSearch, setDebouncedSearch] = React.useState("");

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(filters.search);
    }, 300);
    return () => clearTimeout(timer);
  }, [filters.search]);

  const activeFilters = React.useMemo(
    () => ({ ...filters, search: debouncedSearch }),
    [filters, debouncedSearch],
  );

  const setFilter = <K extends keyof CompanyFilters>(
    key: K,
    value: CompanyFilters[K],
  ) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => setFilters(DEFAULT_FILTERS);

  const hasActiveFilters =
    debouncedSearch.length > 0 ||
    filters.handlerId !== null ||
    filters.industry !== null ||
    filters.status !== null ||
    filters.pipelineStage !== null ||
    filters.ownershipType !== null;

  return {
    filters,
    activeFilters,
    setFilter,
    resetFilters,
    hasActiveFilters,
  };
}
