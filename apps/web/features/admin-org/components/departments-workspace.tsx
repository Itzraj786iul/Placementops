"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  useAdminDepartments,
  useAdminOrgMutations,
} from "@/features/admin-org/hooks/use-admin-org";
import { cn } from "@/lib/utils";

export function DepartmentsWorkspace() {
  const [search, setSearch] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [showForm, setShowForm] = React.useState(false);
  const [editingId, setEditingId] = React.useState<string | null>(null);
  const [name, setName] = React.useState("");
  const [code, setCode] = React.useState("");
  const [description, setDescription] = React.useState("");
  const [displayOrder, setDisplayOrder] = React.useState("0");

  const query = useAdminDepartments({
    search: search || undefined,
    status: status || undefined,
    page,
    pageSize: 20,
  });
  const { createDepartment, updateDepartment } = useAdminOrgMutations();
  const items = query.data?.items ?? [];

  const resetForm = () => {
    setName("");
    setCode("");
    setDescription("");
    setDisplayOrder("0");
    setShowForm(false);
    setEditingId(null);
  };

  const startEdit = (dept: (typeof items)[number]) => {
    setEditingId(dept.id);
    setShowForm(true);
    setName(dept.name);
    setCode(dept.code);
    setDescription(dept.description ?? "");
    setDisplayOrder(String(dept.display_order ?? 0));
  };

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">Departments</h1>
          <p className="text-muted-foreground text-xs">
            {query.data ? `${query.data.total} departments` : "Loading…"}
          </p>
        </div>
        <Input
          className="max-w-xs"
          placeholder="Search name or code…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <Select
          className="w-36"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="archived">Archived</option>
        </Select>
        <Button
          type="button"
          onClick={() => {
            if (showForm) resetForm();
            else {
              setEditingId(null);
              setShowForm(true);
            }
          }}
        >
          {showForm ? "Cancel" : "New department"}
        </Button>
      </header>

      {showForm && (
        <form
          className="grid gap-3 border-b p-4 md:grid-cols-4"
          onSubmit={async (e) => {
            e.preventDefault();
            try {
              if (editingId) {
                await updateDepartment.mutateAsync({
                  id: editingId,
                  payload: {
                    name: name.trim(),
                    code: code.trim(),
                    description: description.trim() || null,
                    display_order: Number(displayOrder) || 0,
                  },
                });
                toast.success("Department updated");
              } else {
                await createDepartment.mutateAsync({
                  name: name.trim(),
                  code: code.trim(),
                  description: description.trim() || undefined,
                  display_order: Number(displayOrder) || 0,
                });
                toast.success("Department created");
              }
              resetForm();
            } catch (err) {
              toast.error(
                err instanceof Error
                  ? err.message
                  : editingId
                    ? "Update failed"
                    : "Create failed",
              );
            }
          }}
        >
          <Input
            required
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            required
            placeholder="Code (e.g. CSE)"
            value={code}
            onChange={(e) => setCode(e.target.value)}
          />
          <Input
            type="number"
            placeholder="Display order"
            value={displayOrder}
            onChange={(e) => setDisplayOrder(e.target.value)}
          />
          <Button
            type="submit"
            disabled={createDepartment.isPending || updateDepartment.isPending}
          >
            {editingId ? "Save" : "Create"}
          </Button>
          <Textarea
            className="md:col-span-4"
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <p className="text-muted-foreground text-xs md:col-span-4">
            Logo upload is reserved for a future release.
          </p>
        </form>
      )}

      <div className="hidden min-h-0 flex-1 overflow-auto md:block">
        <table className="w-full min-w-[800px] border-collapse text-sm">
          <thead className="bg-background sticky top-0 border-b text-left text-xs">
            <tr className="text-muted-foreground">
              <th className="px-4 py-3">Department</th>
              <th className="px-4 py-3">Code</th>
              <th className="px-4 py-3">Students</th>
              <th className="px-4 py-3">Conveners</th>
              <th className="px-4 py-3">Companies</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {query.isLoading &&
              Array.from({ length: 6 }).map((_, i) => (
                <tr key={i} className="border-b">
                  <td colSpan={7} className="px-4 py-3">
                    <div className="bg-muted h-8 animate-pulse rounded" />
                  </td>
                </tr>
              ))}
            {!query.isLoading && items.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="text-muted-foreground px-4 py-12 text-center"
                >
                  No departments found.
                </td>
              </tr>
            )}
            {items.map((dept) => (
              <tr key={dept.id} className="border-b">
                <td className="px-4 py-3 font-medium">{dept.name}</td>
                <td className="px-4 py-3">{dept.code}</td>
                <td className="px-4 py-3">{dept.student_count}</td>
                <td className="px-4 py-3">{dept.convener_count}</td>
                <td className="px-4 py-3">{dept.company_count}</td>
                <td className="px-4 py-3 capitalize">{dept.status}</td>
                <td className="space-x-2 px-4 py-3">
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => startEdit(dept)}
                  >
                    Edit
                  </Button>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={updateDepartment.isPending}
                    onClick={async () => {
                      const next =
                        dept.status === "archived" ? "active" : "archived";
                      const label = next === "archived" ? "Archive" : "Restore";
                      if (!window.confirm(`${label} ${dept.name}?`)) return;
                      try {
                        await updateDepartment.mutateAsync({
                          id: dept.id,
                          payload: { status: next },
                        });
                        toast.success(`${label}d`);
                      } catch (err) {
                        toast.error(
                          err instanceof Error ? err.message : "Update failed",
                        );
                      }
                    }}
                  >
                    {dept.status === "archived" ? "Restore" : "Archive"}
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="grid gap-3 overflow-auto p-4 md:hidden">
        {items.map((dept) => (
          <div key={dept.id} className="rounded-lg border p-4">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-medium">{dept.name}</p>
                <p className="text-muted-foreground text-xs">{dept.code}</p>
              </div>
              <span
                className={cn(
                  "rounded px-2 py-0.5 text-xs capitalize",
                  dept.status === "active" ? "bg-muted" : "bg-destructive/10",
                )}
              >
                {dept.status}
              </span>
            </div>
            <p className="text-muted-foreground mt-2 text-xs">
              Students {dept.student_count} · Conveners {dept.convener_count} ·
              Companies {dept.company_count}
            </p>
          </div>
        ))}
      </div>

      <div className="flex items-center justify-between border-t px-4 py-2 text-sm">
        <span className="text-muted-foreground">
          Page {page} of {query.data?.total_pages || 1}
        </span>
        <div className="flex gap-2">
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <Button
            type="button"
            size="sm"
            variant="outline"
            disabled={!query.data || page >= query.data.total_pages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      </div>
    </div>
  );
}
