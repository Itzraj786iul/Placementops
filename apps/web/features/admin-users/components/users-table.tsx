"use client";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import type { AdminUserListItem } from "@/features/admin-users/types";
import { cn } from "@/lib/utils";

type UsersTableProps = {
  items: AdminUserListItem[];
  selectedIds: Set<string>;
  activeId: string | null;
  isLoading: boolean;
  sortBy: string;
  sortOrder: "asc" | "desc";
  onSort: (field: string) => void;
  onToggle: (id: string) => void;
  onToggleAll: () => void;
  onSelect: (id: string) => void;
};

function initials(name: string) {
  return name
    .split(" ")
    .filter(Boolean)
    .slice(0, 2)
    .map((p) => p[0]?.toUpperCase() ?? "")
    .join("");
}

function formatDate(iso: string | null) {
  if (!iso) return "—";
  return new Date(iso).toLocaleString();
}

export function UsersTable({
  items,
  selectedIds,
  activeId,
  isLoading,
  sortBy,
  sortOrder,
  onSort,
  onToggle,
  onToggleAll,
  onSelect,
}: UsersTableProps) {
  const allSelected =
    items.length > 0 && items.every((i) => selectedIds.has(i.id));

  const SortHeader = ({ field, label }: { field: string; label: string }) => (
    <button
      type="button"
      className="hover:text-foreground inline-flex items-center gap-1"
      onClick={() => onSort(field)}
    >
      {label}
      {sortBy === field && (
        <span className="text-muted-foreground text-[10px]">
          {sortOrder === "asc" ? "↑" : "↓"}
        </span>
      )}
    </button>
  );

  return (
    <div className="h-full overflow-auto">
      <table className="w-full min-w-[960px] border-collapse text-sm">
        <thead className="bg-background sticky top-0 z-10 border-b">
          <tr className="text-muted-foreground text-left text-xs">
            <th className="w-10 px-3 py-3">
              <input
                type="checkbox"
                className="accent-primary h-4 w-4"
                checked={allSelected}
                onChange={() => onToggleAll()}
                aria-label="Select all on page"
              />
            </th>
            <th className="px-3 py-3">User</th>
            <th className="px-3 py-3">
              <SortHeader field="email" label="Email" />
            </th>
            <th className="px-3 py-3">Department</th>
            <th className="px-3 py-3">Role</th>
            <th className="px-3 py-3">
              <SortHeader field="status" label="Status" />
            </th>
            <th className="px-3 py-3">
              <SortHeader field="last_login" label="Last login" />
            </th>
            <th className="px-3 py-3">
              <SortHeader field="created_at" label="Created" />
            </th>
            <th className="px-3 py-3">Actions</th>
          </tr>
        </thead>
        <tbody>
          {isLoading &&
            Array.from({ length: 8 }).map((_, i) => (
              <tr key={`sk-${i}`} className="border-b">
                <td colSpan={9} className="px-3 py-3">
                  <div className="bg-muted h-8 animate-pulse rounded" />
                </td>
              </tr>
            ))}
          {!isLoading && items.length === 0 && (
            <tr>
              <td
                colSpan={9}
                className="text-muted-foreground px-3 py-12 text-center"
              >
                No users match the current filters.
              </td>
            </tr>
          )}
          {!isLoading &&
            items.map((user) => (
              <tr
                key={user.id}
                className={cn(
                  "hover:bg-muted/40 border-b transition-colors",
                  activeId === user.id && "bg-muted/60",
                )}
              >
                <td className="px-3 py-2">
                  <input
                    type="checkbox"
                    className="accent-primary h-4 w-4"
                    checked={selectedIds.has(user.id)}
                    onChange={() => onToggle(user.id)}
                    aria-label={`Select ${user.display_name}`}
                  />
                </td>
                <td className="px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Avatar className="h-8 w-8">
                      {user.profile_picture && (
                        <AvatarImage
                          src={user.profile_picture}
                          alt={user.display_name}
                        />
                      )}
                      <AvatarFallback className="text-[10px]">
                        {initials(user.display_name)}
                      </AvatarFallback>
                    </Avatar>
                    <div>
                      <p className="font-medium">{user.display_name}</p>
                      <p className="text-muted-foreground text-xs">
                        {user.roll_number ?? "—"}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-3 py-2">{user.college_email}</td>
                <td className="px-3 py-2">
                  {user.department_code ?? user.department_name ?? "—"}
                </td>
                <td className="px-3 py-2">
                  {(user.primary_role ??
                    user.roles.map((r) => r.name).join(", ")) ||
                    "—"}
                </td>
                <td className="px-3 py-2 capitalize">{user.status}</td>
                <td className="px-3 py-2 text-xs">
                  {formatDate(user.last_login)}
                </td>
                <td className="px-3 py-2 text-xs">
                  {formatDate(user.created_at)}
                </td>
                <td className="px-3 py-2">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => onSelect(user.id)}
                  >
                    View
                  </Button>
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  );
}
