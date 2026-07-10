"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { downloadOpportunityExport } from "@/features/convener-opportunities/export/export-client";
import {
  DEFAULT_EXPORT_COLUMNS,
  EXPORT_COLUMN_OPTIONS,
  type ExportColumn,
  type ExportFormat,
  type ExportScope,
} from "@/features/convener-opportunities/export/types";
import { usePersistedExportColumns } from "@/features/convener-opportunities/export/use-persisted-columns";
import { APPLICATION_STATUS_OPTIONS } from "@/features/convener-opportunities/constants";
import { APPLICATION_STATUS_LABELS } from "@/features/student-opportunities/constants";
import { ApiError } from "@/lib/api-client";

type ExportDialogProps = {
  open: boolean;
  opportunityId: string;
  companyId: string;
  companyName: string;
  departments: string[];
  onClose: () => void;
};

export function ExportDialog({
  open,
  opportunityId,
  companyId,
  companyName,
  departments,
  onClose,
}: ExportDialogProps) {
  const { columns, persistColumns, hydrated } = usePersistedExportColumns();
  const [format, setFormat] = React.useState<ExportFormat>("xlsx");
  const [scope, setScope] = React.useState<ExportScope>("all");
  const [status, setStatus] = React.useState<string>("");
  const [department, setDepartment] = React.useState<string>("");
  const [includeCompanyFilter, setIncludeCompanyFilter] = React.useState(true);
  const [isExporting, setIsExporting] = React.useState(false);

  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  const toggleColumn = (column: ExportColumn) => {
    const next = columns.includes(column)
      ? columns.filter((item) => item !== column)
      : [...columns, column];
    persistColumns(next.length > 0 ? next : DEFAULT_EXPORT_COLUMNS);
  };

  const handleExport = async () => {
    if (columns.length === 0) {
      toast.error("Select at least one column.");
      return;
    }
    setIsExporting(true);
    try {
      await downloadOpportunityExport(opportunityId, {
        format,
        scope,
        columns,
        filters: {
          status: status ? [status] : null,
          department: department || null,
          company_id: includeCompanyFilter ? companyId : null,
        },
      });
      toast.success("Export downloaded.");
      onClose();
    } catch (error) {
      toast.error(error instanceof ApiError ? error.message : "Export failed.");
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <button
        type="button"
        className="absolute inset-0 bg-black/40"
        aria-label="Close export dialog"
        onClick={onClose}
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="export-dialog-title"
        className="bg-background relative flex max-h-[90vh] w-full max-w-2xl flex-col rounded-lg border shadow-lg"
      >
        <header className="border-b px-6 py-4">
          <h2 id="export-dialog-title" className="text-lg font-semibold">
            Export applications
          </h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Generate a server-side CSV or Excel file for this opportunity.
          </p>
        </header>

        <div className="flex-1 space-y-5 overflow-y-auto px-6 py-4">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                Format
              </label>
              <Select
                value={format}
                onChange={(e) => setFormat(e.target.value as ExportFormat)}
              >
                <option value="xlsx">Excel (XLSX)</option>
                <option value="csv">CSV</option>
              </Select>
            </div>
            <div>
              <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                Scope
              </label>
              <Select
                value={scope}
                onChange={(e) => setScope(e.target.value as ExportScope)}
              >
                <option value="all">All applications</option>
                <option value="eligible">Eligible only</option>
                <option value="ineligible">Ineligible only</option>
              </Select>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                Application status
              </label>
              <Select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
              >
                <option value="">All statuses</option>
                {APPLICATION_STATUS_OPTIONS.map((item) => (
                  <option key={item} value={item}>
                    {APPLICATION_STATUS_LABELS[item]}
                  </option>
                ))}
              </Select>
            </div>
            <div>
              <label className="text-muted-foreground mb-1.5 block text-xs font-medium">
                Department
              </label>
              <Input
                list="export-departments"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                placeholder="All departments"
              />
              <datalist id="export-departments">
                {departments.map((dept) => (
                  <option key={dept} value={dept} />
                ))}
              </datalist>
            </div>
          </div>

          <div className="rounded-lg border p-3">
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-1"
                checked={includeCompanyFilter}
                onChange={(e) => setIncludeCompanyFilter(e.target.checked)}
              />
              <span>
                Restrict to company
                <span className="text-muted-foreground mt-0.5 block text-xs">
                  {companyName}
                </span>
              </span>
            </label>
          </div>

          <div>
            <div className="mb-2 flex items-center justify-between gap-2">
              <p className="text-sm font-medium">Columns</p>
              <Button
                type="button"
                variant="outline"
                size="sm"
                onClick={() => persistColumns(DEFAULT_EXPORT_COLUMNS)}
              >
                Reset defaults
              </Button>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              {EXPORT_COLUMN_OPTIONS.map((option) => (
                <label
                  key={option.value}
                  className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm"
                >
                  <input
                    type="checkbox"
                    checked={
                      hydrated
                        ? columns.includes(option.value)
                        : DEFAULT_EXPORT_COLUMNS.includes(option.value)
                    }
                    onChange={() => toggleColumn(option.value)}
                  />
                  {option.label}
                </label>
              ))}
            </div>
          </div>
        </div>

        <footer className="flex justify-end gap-2 border-t px-6 py-4">
          <Button
            type="button"
            variant="outline"
            onClick={onClose}
            disabled={isExporting}
          >
            Cancel
          </Button>
          <Button type="button" onClick={handleExport} disabled={isExporting}>
            {isExporting ? "Exporting..." : "Download export"}
          </Button>
        </footer>
      </div>
    </div>
  );
}
