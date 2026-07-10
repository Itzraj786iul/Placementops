"use client";

import { ExternalLink } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api-client";

type OpportunityDocument = {
  id: string;
  document_type: string;
  file_url: string;
  uploaded_at: string;
};

const TYPE_LABELS: Record<string, string> = {
  JD: "Job Description (JD)",
  ELIGIBILITY: "Eligibility PDF",
  PPT: "Presentation (PPT)",
  OTHER: "Other documents",
};

type DocumentsTabProps = {
  opportunityId: string;
};

export function DocumentsTab({ opportunityId }: DocumentsTabProps) {
  const query = useQuery({
    queryKey: ["opportunities", opportunityId, "documents"],
    queryFn: () =>
      apiRequest<OpportunityDocument[]>(
        `/opportunities/${opportunityId}/documents`,
      ),
  });

  return (
    <div className="space-y-4 p-4">
      {query.isLoading && (
        <p className="text-muted-foreground text-sm">Loading documents…</p>
      )}
      {query.isError && (
        <p className="text-destructive text-sm">Failed to load documents.</p>
      )}
      {!query.isLoading && (query.data?.length ?? 0) === 0 && (
        <p className="text-muted-foreground text-sm">
          No documents have been uploaded for this opportunity yet.
        </p>
      )}
      <div className="space-y-2">
        {query.data?.map((doc) => (
          <div
            key={doc.id}
            className="flex items-center justify-between rounded-lg border px-4 py-3"
          >
            <div>
              <p className="text-sm font-medium">
                {TYPE_LABELS[doc.document_type] ?? doc.document_type}
              </p>
              <p className="text-muted-foreground text-xs">
                {new Date(doc.uploaded_at).toLocaleDateString()}
              </p>
            </div>
            <a
              href={doc.file_url}
              target="_blank"
              rel="noopener noreferrer"
              aria-label="Open document"
            >
              <ExternalLink className="text-muted-foreground h-4 w-4" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
