"use client";

import * as React from "react";

import type { CompanyDocument } from "@/features/company-crm/types";

export function useDocumentCache() {
  const [cache, setCache] = React.useState<Record<string, CompanyDocument[]>>(
    {},
  );

  const addDocument = React.useCallback((doc: CompanyDocument) => {
    setCache((prev) => ({
      ...prev,
      [doc.company_id]: [doc, ...(prev[doc.company_id] ?? [])],
    }));
  }, []);

  const getDocuments = React.useCallback(
    (companyId: string) => cache[companyId] ?? [],
    [cache],
  );

  return { addDocument, getDocuments };
}
