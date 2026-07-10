"use client";

import * as React from "react";

import {
  DEFAULT_EXPORT_COLUMNS,
  EXPORT_COLUMN_OPTIONS,
  EXPORT_COLUMNS_STORAGE_KEY,
  type ExportColumn,
} from "@/features/convener-opportunities/export/types";

function isExportColumn(value: string): value is ExportColumn {
  return EXPORT_COLUMN_OPTIONS.some((option) => option.value === value);
}

export function usePersistedExportColumns() {
  const [columns, setColumns] = React.useState<ExportColumn[]>(
    DEFAULT_EXPORT_COLUMNS,
  );
  const [hydrated, setHydrated] = React.useState(false);

  React.useEffect(() => {
    try {
      const raw = localStorage.getItem(EXPORT_COLUMNS_STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as string[];
        const valid = parsed.filter(isExportColumn);
        if (valid.length > 0) setColumns(valid);
      }
    } catch {
      // ignore corrupt storage
    }
    setHydrated(true);
  }, []);

  const persistColumns = React.useCallback((next: ExportColumn[]) => {
    setColumns(next);
    try {
      localStorage.setItem(EXPORT_COLUMNS_STORAGE_KEY, JSON.stringify(next));
    } catch {
      // ignore quota errors
    }
  }, []);

  return { columns, persistColumns, hydrated };
}
