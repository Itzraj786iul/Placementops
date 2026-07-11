"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import {
  ROLE_OPTIONS,
  STATUS_OPTIONS,
  type AdminUserFilters,
} from "@/features/admin-users/types";
import { useDepartments } from "@/features/student-onboarding/hooks/use-student-data";

type AdminFilterSidebarProps = {
  filters: AdminUserFilters;
  onChange: <K extends keyof AdminUserFilters>(
    key: K,
    value: AdminUserFilters[K],
  ) => void;
  onReset: () => void;
};

export function AdminFilterSidebar({
  filters,
  onChange,
  onReset,
}: AdminFilterSidebarProps) {
  const departments = useDepartments();

  return (
    <aside className="flex h-full flex-col gap-4 overflow-y-auto border-r p-4">
      <div>
        <h2 className="text-sm font-semibold">Filters</h2>
        <p className="text-muted-foreground text-xs">
          Narrow the user directory
        </p>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium" htmlFor="admin-search">
          Search
        </label>
        <Input
          id="admin-search"
          value={filters.search}
          placeholder="Name, email, roll, dept…"
          onChange={(e) => onChange("search", e.target.value)}
        />
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium" htmlFor="admin-role">
          Role
        </label>
        <Select
          id="admin-role"
          value={filters.role}
          onChange={(e) => onChange("role", e.target.value)}
        >
          <option value="">All roles</option>
          {ROLE_OPTIONS.map((role) => (
            <option key={role} value={role}>
              {role}
            </option>
          ))}
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium" htmlFor="admin-status">
          Status
        </label>
        <Select
          id="admin-status"
          value={filters.status}
          onChange={(e) => onChange("status", e.target.value)}
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium" htmlFor="admin-dept">
          Department
        </label>
        <Select
          id="admin-dept"
          value={filters.departmentId}
          onChange={(e) => onChange("departmentId", e.target.value)}
        >
          <option value="">All departments</option>
          {(departments.data ?? []).map((d) => (
            <option key={d.id} value={d.id}>
              {d.code} — {d.name}
            </option>
          ))}
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium" htmlFor="admin-verification">
          Verification
        </label>
        <Select
          id="admin-verification"
          value={filters.verification}
          onChange={(e) => onChange("verification", e.target.value)}
        >
          <option value="">All</option>
          <option value="PENDING">PENDING</option>
          <option value="VERIFIED">VERIFIED</option>
          <option value="REJECTED">REJECTED</option>
        </Select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-medium" htmlFor="admin-grad">
          Graduation year
        </label>
        <Input
          id="admin-grad"
          type="number"
          placeholder="e.g. 2026"
          value={filters.graduationYear}
          onChange={(e) => onChange("graduationYear", e.target.value)}
        />
      </div>

      <Button type="button" variant="outline" onClick={onReset}>
        Reset filters
      </Button>
    </aside>
  );
}
