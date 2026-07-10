"use client";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Select } from "@/components/ui/select";
import { SearchBar } from "@/features/company-crm/components/search-bar";
import {
  COMPANY_STATUSES,
  OWNERSHIP_TYPES,
  OWNERSHIP_LABELS,
  PIPELINE_LABELS,
  PIPELINE_STAGES,
} from "@/features/company-crm/constants";
import type { CompanyFilters } from "@/features/company-crm/types";
import { Button } from "@/components/ui/button";

type FilterSidebarProps = {
  filters: CompanyFilters;
  onFilterChange: <K extends keyof CompanyFilters>(
    key: K,
    value: CompanyFilters[K],
  ) => void;
  onReset: () => void;
  industries: string[];
  handlers: { id: string; label: string }[];
  hasActiveFilters: boolean;
};

function DisabledFilter({ label }: { label: string }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            {label}
          </label>
          <Select disabled className="opacity-50">
            <option>Coming soon</option>
          </Select>
        </div>
      </TooltipTrigger>
      <TooltipContent>Available in a future update.</TooltipContent>
    </Tooltip>
  );
}

export function FilterSidebar({
  filters,
  onFilterChange,
  onReset,
  industries,
  handlers,
  hasActiveFilters,
}: FilterSidebarProps) {
  return (
    <aside className="bg-muted/20 flex h-full flex-col border-r">
      <div className="border-b p-4">
        <h2 className="text-sm font-semibold">Filters</h2>
        <p className="text-muted-foreground text-xs">
          Refine your company list
        </p>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <SearchBar
          value={filters.search}
          onChange={(v) => onFilterChange("search", v)}
        />

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Handler
          </label>
          <Select
            value={filters.handlerId ?? ""}
            onChange={(e) =>
              onFilterChange("handlerId", e.target.value || null)
            }
          >
            <option value="">All handlers</option>
            {handlers.map((h) => (
              <option key={h.id} value={h.id}>
                {h.label}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Industry
          </label>
          <Select
            value={filters.industry ?? ""}
            onChange={(e) => onFilterChange("industry", e.target.value || null)}
          >
            <option value="">All industries</option>
            {industries.map((ind) => (
              <option key={ind} value={ind}>
                {ind}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Company Status
          </label>
          <Select
            value={filters.status ?? ""}
            onChange={(e) =>
              onFilterChange(
                "status",
                (e.target.value as CompanyFilters["status"]) || null,
              )
            }
          >
            <option value="">All statuses</option>
            {COMPANY_STATUSES.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Pipeline Stage
          </label>
          <Select
            value={filters.pipelineStage ?? ""}
            onChange={(e) =>
              onFilterChange(
                "pipelineStage",
                (e.target.value as CompanyFilters["pipelineStage"]) || null,
              )
            }
          >
            <option value="">All stages</option>
            {PIPELINE_STAGES.map((s) => (
              <option key={s} value={s}>
                {PIPELINE_LABELS[s]}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Ownership Type
          </label>
          <Select
            value={filters.ownershipType ?? ""}
            onChange={(e) =>
              onFilterChange(
                "ownershipType",
                (e.target.value as CompanyFilters["ownershipType"]) || null,
              )
            }
          >
            <option value="">All types</option>
            {OWNERSHIP_TYPES.map((t) => (
              <option key={t} value={t}>
                {OWNERSHIP_LABELS[t]}
              </option>
            ))}
          </Select>
        </div>

        <DisabledFilter label="Hiring Frequency" />

        <div className="rounded-md border border-dashed p-3">
          <p className="text-muted-foreground text-xs font-medium">
            Saved filters
          </p>
          <p className="text-muted-foreground mt-1 text-xs">
            Available in a future update.
          </p>
        </div>
      </div>
      {hasActiveFilters && (
        <div className="border-t p-4">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="w-full"
            onClick={onReset}
          >
            Clear filters
          </Button>
        </div>
      )}
    </aside>
  );
}
