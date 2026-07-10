"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import {
  confirmShortlistImport,
  previewShortlistImport,
} from "@/features/convener-opportunities/import/import-client";
import {
  IMPORTABLE_STATUS_OPTIONS,
  MATCH_FIELD_OPTIONS,
  ROW_MATCH_STATUS_LABELS,
  type ImportPreviewResponse,
  type ImportableStatus,
  type MatchField,
  type RowMatchStatus,
} from "@/features/convener-opportunities/import/types";
import { APPLICATION_STATUS_LABELS } from "@/features/student-opportunities/constants";
import { ApiError } from "@/lib/api-client";

type ImportDialogProps = {
  open: boolean;
  opportunityId: string;
  onClose: () => void;
  onApplied: () => void;
};

type Step = "upload" | "preview" | "done";

const PREVIEW_FILTERS: Array<RowMatchStatus | "ALL"> = [
  "ALL",
  "MATCHED",
  "UNMATCHED",
  "DUPLICATE",
  "INVALID",
];

export function ImportDialog({
  open,
  opportunityId,
  onClose,
  onApplied,
}: ImportDialogProps) {
  const [step, setStep] = React.useState<Step>("upload");
  const [file, setFile] = React.useState<File | null>(null);
  const [matchField, setMatchField] = React.useState<MatchField>("ROLL_NUMBER");
  const [targetStatus, setTargetStatus] =
    React.useState<ImportableStatus>("SHORTLISTED");
  const [preview, setPreview] = React.useState<ImportPreviewResponse | null>(
    null,
  );
  const [filter, setFilter] = React.useState<RowMatchStatus | "ALL">("ALL");
  const [isWorking, setIsWorking] = React.useState(false);
  const [confirmResult, setConfirmResult] = React.useState<{
    rows_updated: number;
    rows_skipped: number;
  } | null>(null);

  React.useEffect(() => {
    if (!open) return;
    setStep("upload");
    setFile(null);
    setPreview(null);
    setFilter("ALL");
    setConfirmResult(null);
    setIsWorking(false);
  }, [open]);

  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isWorking) onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose, isWorking]);

  if (!open) return null;

  const handlePreview = async () => {
    if (!file) {
      toast.error("Choose a CSV or XLSX file.");
      return;
    }
    setIsWorking(true);
    try {
      const result = await previewShortlistImport(
        opportunityId,
        file,
        matchField,
        targetStatus,
      );
      setPreview(result);
      setStep("preview");
    } catch (error) {
      toast.error(
        error instanceof ApiError ? error.message : "Preview failed.",
      );
    } finally {
      setIsWorking(false);
    }
  };

  const handleConfirm = async () => {
    if (!preview) return;
    setIsWorking(true);
    try {
      const result = await confirmShortlistImport(opportunityId, preview.id);
      setConfirmResult({
        rows_updated: result.rows_updated,
        rows_skipped: result.rows_skipped,
      });
      setStep("done");
      onApplied();
      toast.success(
        `Updated ${result.rows_updated} application${result.rows_updated === 1 ? "" : "s"}.`,
      );
    } catch (error) {
      toast.error(
        error instanceof ApiError ? error.message : "Confirm failed.",
      );
    } finally {
      setIsWorking(false);
    }
  };

  const visibleRows =
    preview?.rows.filter(
      (row) => filter === "ALL" || row.match_status === filter,
    ) ?? [];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/40"
        aria-label="Close import dialog"
        onClick={() => {
          if (!isWorking) onClose();
        }}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="import-dialog-title"
        className="bg-background relative flex max-h-[90vh] w-full max-w-3xl flex-col rounded-lg border shadow-lg"
      >
        <header className="border-b px-6 py-4">
          <h2 id="import-dialog-title" className="text-lg font-semibold">
            Import shortlist
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Upload a company shortlist, preview matches, then apply status
            updates.
          </p>
        </header>

        <div className="flex-1 space-y-5 overflow-y-auto px-6 py-4">
          {step === "upload" && (
            <>
              <div>
                <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                  File (CSV or XLSX)
                </label>
                <input
                  type="file"
                  accept=".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                  className="file:bg-secondary block w-full text-sm file:mr-3 file:rounded-md file:border-0 file:px-3 file:py-1.5 file:text-sm"
                  onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                />
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                    Match by
                  </label>
                  <Select
                    value={matchField}
                    onChange={(e) =>
                      setMatchField(e.target.value as MatchField)
                    }
                  >
                    {MATCH_FIELD_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </Select>
                </div>
                <div>
                  <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                    Target status
                  </label>
                  <Select
                    value={targetStatus}
                    onChange={(e) =>
                      setTargetStatus(e.target.value as ImportableStatus)
                    }
                  >
                    {IMPORTABLE_STATUS_OPTIONS.map((status) => (
                      <option key={status} value={status}>
                        {APPLICATION_STATUS_LABELS[status]}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>
            </>
          )}

          {step === "preview" && preview && (
            <>
              <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
                {(
                  [
                    ["Total", preview.total_rows],
                    ["Matched", preview.matched_rows],
                    ["Unmatched", preview.unmatched_rows],
                    ["Duplicates", preview.duplicate_rows],
                    ["Invalid", preview.invalid_rows],
                  ] as const
                ).map(([label, value]) => (
                  <div key={label} className="rounded-md border px-3 py-2">
                    <p className="text-muted-foreground text-xs">{label}</p>
                    <p className="text-lg font-semibold tabular-nums">
                      {value}
                    </p>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                {PREVIEW_FILTERS.map((item) => (
                  <Button
                    key={item}
                    type="button"
                    size="sm"
                    variant={filter === item ? "default" : "outline"}
                    onClick={() => setFilter(item)}
                  >
                    {item === "ALL" ? "All" : ROW_MATCH_STATUS_LABELS[item]}
                  </Button>
                ))}
              </div>

              <div className="overflow-x-auto rounded-md border">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <thead className="bg-muted/40 text-muted-foreground border-b text-xs">
                    <tr>
                      <th className="px-3 py-2 font-medium">Row</th>
                      <th className="px-3 py-2 font-medium">Identifier</th>
                      <th className="px-3 py-2 font-medium">Status</th>
                      <th className="px-3 py-2 font-medium">Student</th>
                      <th className="px-3 py-2 font-medium">Current</th>
                      <th className="px-3 py-2 font-medium">Note</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleRows.length === 0 ? (
                      <tr>
                        <td
                          colSpan={6}
                          className="text-muted-foreground px-3 py-6 text-center"
                        >
                          No rows in this category.
                        </td>
                      </tr>
                    ) : (
                      visibleRows.map((row) => (
                        <tr key={row.id} className="border-b last:border-0">
                          <td className="px-3 py-2 tabular-nums">
                            {row.row_number}
                          </td>
                          <td className="px-3 py-2 font-mono text-xs">
                            {row.raw_identifier || "—"}
                          </td>
                          <td className="px-3 py-2">
                            {ROW_MATCH_STATUS_LABELS[row.match_status]}
                          </td>
                          <td className="px-3 py-2">
                            {row.student_name ?? "—"}
                          </td>
                          <td className="px-3 py-2">
                            {row.current_status
                              ? (APPLICATION_STATUS_LABELS[
                                  row.current_status as keyof typeof APPLICATION_STATUS_LABELS
                                ] ?? row.current_status)
                              : "—"}
                          </td>
                          <td className="text-muted-foreground px-3 py-2">
                            {row.message ?? "—"}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>

              <p className="text-muted-foreground text-xs">
                No statuses are changed until you confirm. Target:{" "}
                {APPLICATION_STATUS_LABELS[preview.target_status]}.
              </p>
            </>
          )}

          {step === "done" && confirmResult && (
            <div className="space-y-2 rounded-md border px-4 py-5">
              <p className="font-medium">Import applied</p>
              <p className="text-muted-foreground text-sm">
                Rows updated: {confirmResult.rows_updated}. Rows skipped:{" "}
                {confirmResult.rows_skipped}.
              </p>
            </div>
          )}
        </div>

        <footer className="flex justify-end gap-2 border-t px-6 py-4">
          {step === "upload" && (
            <>
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isWorking}
              >
                Cancel
              </Button>
              <Button
                type="button"
                onClick={handlePreview}
                disabled={isWorking || !file}
              >
                {isWorking ? "Parsing..." : "Preview"}
              </Button>
            </>
          )}
          {step === "preview" && (
            <>
              <Button
                type="button"
                variant="outline"
                onClick={() => setStep("upload")}
                disabled={isWorking}
              >
                Back
              </Button>
              <Button
                type="button"
                onClick={handleConfirm}
                disabled={isWorking || (preview?.matched_rows ?? 0) === 0}
              >
                {isWorking ? "Applying..." : "Confirm & update"}
              </Button>
            </>
          )}
          {step === "done" && (
            <Button type="button" onClick={onClose}>
              Close
            </Button>
          )}
        </footer>
      </div>
    </div>
  );
}
