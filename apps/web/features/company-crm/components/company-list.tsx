"use client";

import { useMemo } from "react";

import { CompanyCard } from "@/features/company-crm/components/company-card";
import { CrmEmptyState } from "@/features/company-crm/components/empty-state";
import { CompanyListSkeleton } from "@/features/company-crm/components/loading-skeleton";
import type { CompanyListItem } from "@/features/company-crm/types";

type CompanyListProps = {
  companies: CompanyListItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  lastCommMap: Record<string, string | undefined>;
};

export function CompanyList({
  companies,
  selectedId,
  onSelect,
  isLoading,
  isError,
  onRetry,
  lastCommMap,
}: CompanyListProps) {
  const sorted = useMemo(
    () => [...companies].sort((a, b) => a.name.localeCompare(b.name)),
    [companies],
  );

  if (isLoading) return <CompanyListSkeleton />;

  if (isError) {
    return (
      <div className="p-6 text-center">
        <p className="text-destructive text-sm">Failed to load companies.</p>
        <button
          type="button"
          onClick={onRetry}
          className="text-primary mt-2 text-sm underline"
        >
          Retry
        </button>
      </div>
    );
  }

  if (sorted.length === 0) {
    return (
      <div className="p-4">
        <CrmEmptyState
          title="No companies found"
          description="Try adjusting your filters or create a new company."
        />
      </div>
    );
  }

  return (
    <div
      className="space-y-2 overflow-y-auto p-3"
      role="listbox"
      aria-label="Company list"
    >
      {sorted.map((company) => (
        <CompanyCard
          key={company.id}
          company={company}
          selected={company.id === selectedId}
          lastCommunication={lastCommMap[company.id]}
          onSelect={onSelect}
        />
      ))}
    </div>
  );
}
