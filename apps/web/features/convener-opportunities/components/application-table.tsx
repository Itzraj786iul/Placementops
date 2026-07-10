"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { ApplicationRow } from "@/features/convener-opportunities/components/application-row";
import { OperationsEmptyState } from "@/features/convener-opportunities/components/empty-state";
import { ApplicationTableSkeleton } from "@/features/convener-opportunities/components/loading-skeleton";
import {
  APPLICATIONS_PAGE_SIZE,
  APPLICATION_STATUS_OPTIONS,
} from "@/features/convener-opportunities/constants";
import { APPLICATION_STATUS_LABELS } from "@/features/student-opportunities/constants";
import type {
  ApplicationSortField,
  EnrichedApplication,
  SortDirection,
} from "@/features/convener-opportunities/types";
import type { ApplicationFilters } from "@/features/convener-opportunities/types";

type ApplicationTableProps = {
  items: EnrichedApplication[];
  pageItems: EnrichedApplication[];
  totalCount: number;
  page: number;
  pageSize?: number;
  filters: ApplicationFilters;
  sortField: ApplicationSortField;
  sortDirection: SortDirection;
  departments: string[];
  branches: string[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onFilterChange: <K extends keyof ApplicationFilters>(
    key: K,
    value: ApplicationFilters[K],
  ) => void;
  onResetFilters: () => void;
  onToggleSort: (field: ApplicationSortField) => void;
  onPageChange: (page: number) => void;
  onSelectApplication: (applicationId: string) => void;
  hasActiveFilters: boolean;
};

function SortButton({
  label,
  field,
  sortField,
  sortDirection,
  onToggle,
}: {
  label: string;
  field: ApplicationSortField;
  sortField: ApplicationSortField;
  sortDirection: SortDirection;
  onToggle: (field: ApplicationSortField) => void;
}) {
  const active = sortField === field;
  return (
    <button
      type="button"
      className="hover:text-foreground inline-flex items-center gap-1 font-medium"
      onClick={() => onToggle(field)}
      aria-sort={
        active ? (sortDirection === "asc" ? "ascending" : "descending") : "none"
      }
    >
      {label}
      {active && (
        <span aria-hidden="true">{sortDirection === "asc" ? "↑" : "↓"}</span>
      )}
    </button>
  );
}

export function ApplicationTable({
  items,
  pageItems,
  totalCount,
  page,
  pageSize = APPLICATIONS_PAGE_SIZE,
  filters,
  sortField,
  sortDirection,
  departments,
  branches,
  isLoading,
  isError,
  onRetry,
  onFilterChange,
  onResetFilters,
  onToggleSort,
  onPageChange,
  onSelectApplication,
  hasActiveFilters,
}: ApplicationTableProps) {
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));

  if (isLoading) return <ApplicationTableSkeleton />;

  if (isError) {
    return (
      <div className="p-6 text-center text-sm">
        <p className="text-destructive">Could not load applications.</p>
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

  return (
    <div className="space-y-4 p-4">
      <div className="flex flex-col gap-3 lg:flex-row lg:items-end">
        <div className="flex-1">
          <label
            htmlFor="app-search"
            className="text-muted-foreground mb-1.5 block text-xs font-medium"
          >
            Search
          </label>
          <Input
            id="app-search"
            value={filters.search}
            onChange={(e) => onFilterChange("search", e.target.value)}
            placeholder="Name, roll number, department..."
          />
        </div>
        <div className="grid flex-1 gap-3 sm:grid-cols-3">
          <div>
            <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
              Status
            </label>
            <Select
              value={filters.status ?? ""}
              onChange={(e) =>
                onFilterChange(
                  "status",
                  (e.target.value || null) as ApplicationFilters["status"],
                )
              }
            >
              <option value="">All statuses</option>
              {APPLICATION_STATUS_OPTIONS.map((status) => (
                <option key={status} value={status}>
                  {APPLICATION_STATUS_LABELS[status]}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
              Department
            </label>
            <Select
              value={filters.department ?? ""}
              onChange={(e) =>
                onFilterChange("department", e.target.value || null)
              }
            >
              <option value="">All departments</option>
              {departments.map((dept) => (
                <option key={dept} value={dept}>
                  {dept}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
              Branch
            </label>
            <Select
              value={filters.branch ?? ""}
              onChange={(e) => onFilterChange("branch", e.target.value || null)}
            >
              <option value="">All branches</option>
              {branches.map((branch) => (
                <option key={branch} value={branch}>
                  {branch}
                </option>
              ))}
            </Select>
          </div>
        </div>
      </div>

      {hasActiveFilters && (
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={onResetFilters}
        >
          Clear filters
        </Button>
      )}

      {items.length === 0 ? (
        <OperationsEmptyState
          title="No applications yet"
          description="Applications will appear here once students apply to this opportunity."
        />
      ) : pageItems.length === 0 ? (
        <OperationsEmptyState
          title="No matching applications"
          description="Try adjusting your search or filters."
        />
      ) : (
        <div className="overflow-x-auto rounded-lg border">
          <table className="w-full min-w-[900px] text-left">
            <thead className="bg-muted/30 text-muted-foreground border-b text-xs">
              <tr>
                <th className="px-4 py-3">
                  <SortButton
                    label="Student"
                    field="name"
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onToggle={onToggleSort}
                  />
                </th>
                <th className="px-4 py-3">
                  <SortButton
                    label="Roll No."
                    field="roll_number"
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onToggle={onToggleSort}
                  />
                </th>
                <th className="px-4 py-3">
                  <SortButton
                    label="Department"
                    field="department"
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onToggle={onToggleSort}
                  />
                </th>
                <th className="px-4 py-3">
                  <SortButton
                    label="CGPA"
                    field="cgpa"
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onToggle={onToggleSort}
                  />
                </th>
                <th className="px-4 py-3">Resume</th>
                <th className="px-4 py-3">
                  <SortButton
                    label="Applied At"
                    field="applied_at"
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onToggle={onToggleSort}
                  />
                </th>
                <th className="px-4 py-3">
                  <SortButton
                    label="Status"
                    field="status"
                    sortField={sortField}
                    sortDirection={sortDirection}
                    onToggle={onToggleSort}
                  />
                </th>
              </tr>
            </thead>
            <tbody>
              {pageItems.map((item) => (
                <ApplicationRow
                  key={item.application.id}
                  item={item}
                  onSelect={onSelectApplication}
                />
              ))}
            </tbody>
          </table>
        </div>
      )}

      {totalCount > pageSize && (
        <div className="flex items-center justify-between text-sm">
          <p className="text-muted-foreground">
            Showing {(page - 1) * pageSize + 1}–
            {Math.min(page * pageSize, totalCount)} of {totalCount}
          </p>
          <div className="flex gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={page <= 1}
              onClick={() => onPageChange(page - 1)}
            >
              Previous
            </Button>
            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={page >= totalPages}
              onClick={() => onPageChange(page + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
