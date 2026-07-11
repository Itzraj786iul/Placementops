"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import {
  useAdminOrgMutations,
  useAdminSeasons,
} from "@/features/admin-org/hooks/use-admin-org";

export function SeasonsWorkspace() {
  const [search, setSearch] = React.useState("");
  const [status, setStatus] = React.useState("");
  const [page, setPage] = React.useState(1);
  const [showForm, setShowForm] = React.useState(false);
  const [name, setName] = React.useState("");
  const [batch, setBatch] = React.useState("");
  const [startDate, setStartDate] = React.useState("");
  const [endDate, setEndDate] = React.useState("");
  const [description, setDescription] = React.useState("");

  const query = useAdminSeasons({
    search: search || undefined,
    status: status || undefined,
    page,
    pageSize: 20,
  });
  const { createSeason, updateSeason, activateSeason } = useAdminOrgMutations();
  const items = query.data?.items ?? [];
  const current = items.find((s) => s.is_current);

  return (
    <div className="-m-6 flex h-[calc(100vh-4rem)] flex-col">
      <header className="flex flex-wrap items-center gap-3 border-b px-4 py-3">
        <div className="min-w-0 flex-1">
          <h1 className="text-lg font-semibold">Placement Seasons</h1>
          <p className="text-muted-foreground text-xs">
            {current
              ? `Current: ${current.name} (${current.academic_batch})`
              : "No active season"}
          </p>
        </div>
        <Input
          className="max-w-xs"
          placeholder="Search seasons…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(1);
          }}
        />
        <Select
          className="w-40"
          value={status}
          onChange={(e) => {
            setStatus(e.target.value);
            setPage(1);
          }}
        >
          <option value="">All statuses</option>
          <option value="planning">Planning</option>
          <option value="active">Active</option>
          <option value="completed">Completed</option>
          <option value="archived">Archived</option>
        </Select>
        <Button type="button" onClick={() => setShowForm((v) => !v)}>
          {showForm ? "Cancel" : "New season"}
        </Button>
      </header>

      {current?.stats && (
        <div className="grid grid-cols-2 gap-3 border-b p-4 md:grid-cols-4">
          {(
            [
              ["Applications", current.stats.applications],
              ["Companies", current.stats.companies],
              ["Students", current.stats.students],
              ["Offers", current.stats.offers],
            ] as const
          ).map(([label, value]) => (
            <div key={label} className="rounded-lg border p-3">
              <p className="text-muted-foreground text-xs">{label}</p>
              <p className="text-xl font-semibold">{value}</p>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <form
          className="grid gap-3 border-b p-4 md:grid-cols-4"
          onSubmit={async (e) => {
            e.preventDefault();
            try {
              await createSeason.mutateAsync({
                name: name.trim(),
                academic_batch: batch.trim(),
                start_date: startDate,
                end_date: endDate,
                description: description.trim() || undefined,
              });
              toast.success("Season created");
              setShowForm(false);
              setName("");
              setBatch("");
              setStartDate("");
              setEndDate("");
              setDescription("");
            } catch (err) {
              toast.error(err instanceof Error ? err.message : "Create failed");
            }
          }}
        >
          <Input
            required
            placeholder="Season name (e.g. 2026)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <Input
            required
            placeholder="Academic batch"
            value={batch}
            onChange={(e) => setBatch(e.target.value)}
          />
          <Input
            required
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <Input
            required
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <Textarea
            className="md:col-span-3"
            placeholder="Description (optional)"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <Button type="submit" disabled={createSeason.isPending}>
            Create
          </Button>
        </form>
      )}

      <div className="min-h-0 flex-1 overflow-auto">
        <table className="w-full min-w-[900px] border-collapse text-sm">
          <thead className="bg-background sticky top-0 border-b text-left text-xs">
            <tr className="text-muted-foreground">
              <th className="px-4 py-3">Season</th>
              <th className="px-4 py-3">Batch</th>
              <th className="px-4 py-3">Dates</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Stats</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {query.isLoading &&
              Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="border-b">
                  <td colSpan={6} className="px-4 py-3">
                    <div className="bg-muted h-8 animate-pulse rounded" />
                  </td>
                </tr>
              ))}
            {items.map((season) => (
              <tr key={season.id} className="border-b">
                <td className="px-4 py-3">
                  <p className="font-medium">{season.name}</p>
                  {season.is_current && (
                    <p className="text-muted-foreground text-xs">Current</p>
                  )}
                </td>
                <td className="px-4 py-3">{season.academic_batch}</td>
                <td className="px-4 py-3 text-xs">
                  {season.start_date} → {season.end_date}
                </td>
                <td className="px-4 py-3 capitalize">{season.status}</td>
                <td className="px-4 py-3 text-xs">
                  {season.stats
                    ? `A ${season.stats.applications} · C ${season.stats.companies} · S ${season.stats.students} · O ${season.stats.offers}`
                    : "—"}
                </td>
                <td className="space-x-2 px-4 py-3">
                  {!season.is_current && season.status !== "archived" && (
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={activateSeason.isPending}
                      onClick={async () => {
                        if (
                          !window.confirm(
                            `Activate ${season.name}? This will deactivate the current season.`,
                          )
                        ) {
                          return;
                        }
                        try {
                          await activateSeason.mutateAsync(season.id);
                          toast.success("Season activated");
                        } catch (err) {
                          toast.error(
                            err instanceof Error ? err.message : "Failed",
                          );
                        }
                      }}
                    >
                      Activate
                    </Button>
                  )}
                  {season.status !== "archived" &&
                    season.status !== "completed" && (
                      <Button
                        type="button"
                        size="sm"
                        variant="outline"
                        disabled={updateSeason.isPending || season.read_only}
                        onClick={async () => {
                          if (
                            !window.confirm(`Mark ${season.name} completed?`)
                          ) {
                            return;
                          }
                          try {
                            await updateSeason.mutateAsync({
                              id: season.id,
                              payload: { status: "completed" },
                            });
                            toast.success("Season completed");
                          } catch (err) {
                            toast.error(
                              err instanceof Error ? err.message : "Failed",
                            );
                          }
                        }}
                      >
                        Complete
                      </Button>
                    )}
                  {season.status !== "archived" && (
                    <Button
                      type="button"
                      size="sm"
                      variant="outline"
                      disabled={updateSeason.isPending}
                      onClick={async () => {
                        if (!window.confirm(`Archive ${season.name}?`)) return;
                        try {
                          await updateSeason.mutateAsync({
                            id: season.id,
                            payload: { status: "archived" },
                          });
                          toast.success("Season archived");
                        } catch (err) {
                          toast.error(
                            err instanceof Error ? err.message : "Failed",
                          );
                        }
                      }}
                    >
                      Archive
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
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
