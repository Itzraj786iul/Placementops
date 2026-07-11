"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { AdminFilterSidebar } from "@/features/admin-users/components/admin-filter-sidebar";
import { InviteUserForm } from "@/features/admin-users/components/invite-user-form";
import { UserDetailDrawer } from "@/features/admin-users/components/user-detail-drawer";
import { UsersTable } from "@/features/admin-users/components/users-table";
import {
  useAdminUserMutations,
  useAdminUsers,
} from "@/features/admin-users/hooks/use-admin-users";
import {
  DEFAULT_ADMIN_FILTERS,
  ROLE_OPTIONS,
  type AdminUserFilters,
} from "@/features/admin-users/types";
import { ROLES } from "@/lib/auth/constants";
import { hasRole } from "@/lib/auth/roles";
import { useAuth } from "@/providers/auth-provider";

export function AdminUsersWorkspace() {
  const { user } = useAuth();
  const isSuperAdmin = hasRole(user, ROLES.SUPER_ADMIN);
  const [filters, setFilters] = React.useState<AdminUserFilters>(
    DEFAULT_ADMIN_FILTERS,
  );
  const [selectedIds, setSelectedIds] = React.useState<Set<string>>(new Set());
  const [activeId, setActiveId] = React.useState<string | null>(null);
  const [bulkRole, setBulkRole] = React.useState("STUDENT");
  const [inviteOpen, setInviteOpen] = React.useState(false);

  const query = useAdminUsers(filters);
  const { bulk } = useAdminUserMutations();

  const setFilter = <K extends keyof AdminUserFilters>(
    key: K,
    value: AdminUserFilters[K],
  ) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
      ...(key !== "page" ? { page: 1 } : {}),
    }));
  };

  const items = query.data?.items ?? [];

  const confirmBulk = async (
    action: "activate" | "deactivate" | "assign_role" | "export",
  ) => {
    if (selectedIds.size === 0) {
      toast.error("Select at least one user");
      return;
    }
    const label =
      action === "assign_role"
        ? `assign ${bulkRole} to ${selectedIds.size} user(s)`
        : `${action} ${selectedIds.size} user(s)`;
    if (!window.confirm(`Confirm: ${label}?`)) return;

    try {
      const result = await bulk.mutateAsync({
        user_ids: Array.from(selectedIds),
        action,
        role_name: action === "assign_role" ? bulkRole : undefined,
        confirm: true,
      });
      if (action === "export" && result.export_rows) {
        const blob = new Blob([JSON.stringify(result.export_rows, null, 2)], {
          type: "application/json",
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "users-export.json";
        a.click();
        URL.revokeObjectURL(url);
      }
      toast.success(`Updated ${result.updated}, skipped ${result.skipped}`);
      setSelectedIds(new Set());
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Bulk action failed");
    }
  };

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">User & Role Management</h1>
          <p className="text-muted-foreground text-xs">
            {query.data ? `${query.data.total} users` : "Loading directory…"}
          </p>
        </div>
        <Input
          className="max-w-xs"
          placeholder="Quick search…"
          value={filters.search}
          onChange={(e) => setFilter("search", e.target.value)}
        />
        {isSuperAdmin && (
          <Button type="button" onClick={() => setInviteOpen((v) => !v)}>
            Invite user
          </Button>
        )}
        <Button
          type="button"
          variant="outline"
          onClick={() => void query.refetch()}
          disabled={query.isFetching}
        >
          Refresh
        </Button>
      </header>

      <InviteUserForm
        open={inviteOpen}
        onClose={() => setInviteOpen(false)}
        onInvited={() => void query.refetch()}
      />

      {selectedIds.size > 0 && (
        <div className="bg-muted/40 flex flex-wrap items-center gap-2 border-b px-4 py-2">
          <span className="text-sm">{selectedIds.size} selected</span>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => void confirmBulk("activate")}
          >
            Activate
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => void confirmBulk("deactivate")}
          >
            Deactivate
          </Button>
          <Select
            className="h-8 w-44"
            value={bulkRole}
            onChange={(e) => setBulkRole(e.target.value)}
          >
            {ROLE_OPTIONS.filter(
              (r) => r !== "SUPER_ADMIN" || isSuperAdmin,
            ).map((role) => (
              <option key={role} value={role}>
                {role}
              </option>
            ))}
          </Select>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => void confirmBulk("assign_role")}
          >
            Assign role
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => void confirmBulk("export")}
          >
            Export
          </Button>
        </div>
      )}

      <div className="flex min-h-0 flex-1 overflow-hidden">
        <div className="hidden w-64 shrink-0 lg:block">
          <AdminFilterSidebar
            filters={filters}
            onChange={setFilter}
            onReset={() => setFilters(DEFAULT_ADMIN_FILTERS)}
          />
        </div>

        <div className="flex min-w-0 flex-1 flex-col">
          <UsersTable
            items={items}
            selectedIds={selectedIds}
            activeId={activeId}
            isLoading={query.isLoading}
            sortBy={filters.sortBy}
            sortOrder={filters.sortOrder}
            onSort={(field) => {
              if (filters.sortBy === field) {
                setFilter(
                  "sortOrder",
                  filters.sortOrder === "asc" ? "desc" : "asc",
                );
              } else {
                setFilters((prev) => ({
                  ...prev,
                  sortBy: field,
                  sortOrder: "asc",
                  page: 1,
                }));
              }
            }}
            onToggle={(id) => {
              setSelectedIds((prev) => {
                const next = new Set(prev);
                if (next.has(id)) next.delete(id);
                else next.add(id);
                return next;
              });
            }}
            onToggleAll={() => {
              setSelectedIds((prev) => {
                if (items.every((i) => prev.has(i.id))) return new Set();
                return new Set(items.map((i) => i.id));
              });
            }}
            onSelect={setActiveId}
          />

          <div className="flex items-center justify-between border-t px-4 py-2 text-sm">
            <span className="text-muted-foreground">
              Page {filters.page} of {query.data?.total_pages || 1}
            </span>
            <div className="flex gap-2">
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={filters.page <= 1}
                onClick={() => setFilter("page", filters.page - 1)}
              >
                Previous
              </Button>
              <Button
                type="button"
                size="sm"
                variant="outline"
                disabled={!query.data || filters.page >= query.data.total_pages}
                onClick={() => setFilter("page", filters.page + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </div>
      </div>

      <UserDetailDrawer userId={activeId} onClose={() => setActiveId(null)} />
    </div>
  );
}
