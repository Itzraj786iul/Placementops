"use client";

import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { Select } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  EMPLOYMENT_LABELS,
  EMPLOYMENT_TYPES,
  MODE_LABELS,
  WORK_MODES,
  APPLICATION_STATUS_LABELS,
} from "@/features/student-opportunities/constants";
import type { OpportunityFilters } from "@/features/student-opportunities/types";

type FilterSidebarProps = {
  filters: OpportunityFilters;
  onFilterChange: <K extends keyof OpportunityFilters>(
    key: K,
    value: OpportunityFilters[K],
  ) => void;
  onReset: () => void;
  locations: string[];
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
      <TooltipContent>Not supported by the backend yet.</TooltipContent>
    </Tooltip>
  );
}

export function FilterSidebar({
  filters,
  onFilterChange,
  onReset,
  locations,
  hasActiveFilters,
}: FilterSidebarProps) {
  return (
    <aside className="bg-muted/20 flex h-full flex-col border-r">
      <div className="border-b p-4">
        <h2 className="text-sm font-semibold">Filters</h2>
        <p className="text-muted-foreground text-xs">Refine opportunities</p>
      </div>
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        <div>
          <label
            htmlFor="opp-search"
            className="text-muted-foreground mb-1.5 block text-xs font-medium"
          >
            Search
          </label>
          <Input
            id="opp-search"
            value={filters.search}
            onChange={(e) => onFilterChange("search", e.target.value)}
            placeholder="Role, title, location..."
            aria-label="Search opportunities"
          />
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Employment Type
          </label>
          <Select
            value={filters.employmentType ?? ""}
            onChange={(e) =>
              onFilterChange(
                "employmentType",
                (e.target.value ||
                  null) as OpportunityFilters["employmentType"],
              )
            }
          >
            <option value="">All types</option>
            {EMPLOYMENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {EMPLOYMENT_LABELS[t]}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Location
          </label>
          <Select
            value={filters.location ?? ""}
            onChange={(e) => onFilterChange("location", e.target.value || null)}
          >
            <option value="">All locations</option>
            {locations.map((loc) => (
              <option key={loc} value={loc}>
                {loc}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Mode
          </label>
          <Select
            value={filters.mode ?? ""}
            onChange={(e) =>
              onFilterChange(
                "mode",
                (e.target.value || null) as OpportunityFilters["mode"],
              )
            }
          >
            <option value="">All modes</option>
            {WORK_MODES.map((m) => (
              <option key={m} value={m}>
                {MODE_LABELS[m]}
              </option>
            ))}
          </Select>
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            CTC min (LPA)
          </label>
          <Input
            type="number"
            min={0}
            value={filters.ctcMin ?? ""}
            onChange={(e) =>
              onFilterChange(
                "ctcMin",
                e.target.value ? Number(e.target.value) : null,
              )
            }
            placeholder="Min"
          />
        </div>

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            CTC max (LPA)
          </label>
          <Input
            type="number"
            min={0}
            value={filters.ctcMax ?? ""}
            onChange={(e) =>
              onFilterChange(
                "ctcMax",
                e.target.value ? Number(e.target.value) : null,
              )
            }
            placeholder="Max"
          />
        </div>

        <DisabledFilter label="Department" />
        <DisabledFilter label="Company" />

        <div>
          <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
            Application Status
          </label>
          <Select
            value={filters.applicationStatus ?? ""}
            onChange={(e) =>
              onFilterChange(
                "applicationStatus",
                (e.target.value ||
                  null) as OpportunityFilters["applicationStatus"],
              )
            }
          >
            <option value="">All</option>
            <option value="NOT_APPLIED">Not applied</option>
            {Object.entries(APPLICATION_STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </Select>
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
