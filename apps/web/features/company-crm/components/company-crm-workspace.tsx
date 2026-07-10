"use client";

import * as React from "react";
import { useMemo } from "react";

import { CompanyDetailPanel } from "@/features/company-crm/components/company-detail-panel";
import { CompanyList } from "@/features/company-crm/components/company-list";
import { CrmHeader } from "@/features/company-crm/components/crm-header";
import { FilterSidebar } from "@/features/company-crm/components/filter-sidebar";
import { NewCompanySheet } from "@/features/company-crm/components/new-company-sheet";
import { useCompaniesList } from "@/features/company-crm/hooks/use-companies";
import { useCompanyFilters } from "@/features/company-crm/hooks/use-company-filters";
import { useCompanyTimeline } from "@/features/company-crm/hooks/use-company-timeline";
import type { CrmTab } from "@/features/company-crm/types";
import {
  extractHandlers,
  extractIndustries,
  filterCompanies,
} from "@/features/company-crm/utils/filter-companies";

export function CompanyCrmWorkspace() {
  const [selectedId, setSelectedId] = React.useState<string | null>(null);
  const [activeTab, setActiveTab] = React.useState<CrmTab>("overview");
  const [newCompanyOpen, setNewCompanyOpen] = React.useState(false);

  const { filters, activeFilters, setFilter, resetFilters, hasActiveFilters } =
    useCompanyFilters();

  const companiesQuery = useCompaniesList();
  const timelineQuery = useCompanyTimeline(selectedId, Boolean(selectedId));

  const filtered = useMemo(() => {
    if (!companiesQuery.data) return [];
    return filterCompanies(companiesQuery.data, activeFilters);
  }, [companiesQuery.data, activeFilters]);

  const industries = useMemo(
    () => extractIndustries(companiesQuery.data ?? []),
    [companiesQuery.data],
  );

  const handlers = useMemo(
    () => extractHandlers(companiesQuery.data ?? []),
    [companiesQuery.data],
  );

  const lastCommMap = useMemo(() => {
    if (!selectedId || !timelineQuery.data?.length) return {};
    return { [selectedId]: timelineQuery.data[0]?.communication_date };
  }, [selectedId, timelineQuery.data]);

  const handleSelect = (id: string) => {
    setSelectedId(id);
    setActiveTab("overview");
  };

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <CrmHeader
        search={filters.search}
        onSearchChange={(v) => setFilter("search", v)}
        onRefresh={() => companiesQuery.refetch()}
        onNewCompany={() => setNewCompanyOpen(true)}
        isRefreshing={companiesQuery.isFetching}
      />

      <div className="flex flex-1 overflow-hidden">
        <div className="hidden w-64 shrink-0 lg:block">
          <FilterSidebar
            filters={filters}
            onFilterChange={setFilter}
            onReset={resetFilters}
            industries={industries}
            handlers={handlers}
            hasActiveFilters={hasActiveFilters}
          />
        </div>

        <div className="flex w-full min-w-0 flex-1 overflow-hidden">
          <section
            className="w-full shrink-0 overflow-hidden border-r md:w-80 lg:w-96"
            aria-label="Company list panel"
          >
            <CompanyList
              companies={filtered}
              selectedId={selectedId}
              onSelect={handleSelect}
              isLoading={companiesQuery.isLoading}
              isError={companiesQuery.isError}
              onRetry={() => companiesQuery.refetch()}
              lastCommMap={lastCommMap}
            />
          </section>

          <section
            className="hidden min-w-0 flex-1 md:block"
            aria-label="Company detail panel"
          >
            <CompanyDetailPanel
              companyId={selectedId}
              activeTab={activeTab}
              onTabChange={setActiveTab}
            />
          </section>

          {selectedId && (
            <section
              className="bg-background fixed inset-0 z-40 md:hidden"
              aria-label="Company detail panel mobile"
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
                  <CompanyDetailPanel
                    companyId={selectedId}
                    activeTab={activeTab}
                    onTabChange={setActiveTab}
                  />
                </div>
              </div>
            </section>
          )}
        </div>
      </div>

      <NewCompanySheet
        open={newCompanyOpen}
        onClose={() => setNewCompanyOpen(false)}
        onCreated={(id) => {
          setSelectedId(id);
          setActiveTab("overview");
        }}
      />
    </div>
  );
}
