"use client";

import { ExternalLink } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import * as React from "react";

import { FileUpload } from "@/components/ui/file-upload";
import { Select } from "@/components/ui/select";
import {
  fetchOpportunityDocuments,
  uploadOpportunityDocument,
  type OpportunityDocument,
} from "@/features/convener-opportunities/api/operations-client";

const DOCUMENT_TYPES = [
  { label: "Job Description (JD)", type: "JD" },
  { label: "Eligibility PDF", type: "ELIGIBILITY" },
  { label: "Presentation (PPT)", type: "PPT" },
  { label: "Other documents", type: "OTHER" },
] as const;

const TYPE_LABELS: Record<string, string> = Object.fromEntries(
  DOCUMENT_TYPES.map((d) => [d.type, d.label]),
);

type DocumentsPanelProps = {
  opportunityId: string;
};

export function DocumentsPanel({ opportunityId }: DocumentsPanelProps) {
  const [docType, setDocType] = React.useState("JD");
  const query = useQuery({
    queryKey: ["opportunities", opportunityId, "documents"],
    queryFn: () => fetchOpportunityDocuments(opportunityId),
  });

  return (
    <div className="space-y-6 p-6">
      <div className="space-y-3">
        <p className="text-sm font-medium">Upload document</p>
        <Select value={docType} onChange={(e) => setDocType(e.target.value)}>
          {DOCUMENT_TYPES.map((doc) => (
            <option key={doc.type} value={doc.type}>
              {doc.label}
            </option>
          ))}
        </Select>
        <FileUpload
          category="document"
          hint="PDF, DOC, DOCX, PNG, JPG · max 10 MB"
          onUpload={async (file, onProgress) => {
            await uploadOpportunityDocument(
              opportunityId,
              file,
              docType,
              onProgress,
            );
            toast.success("Document uploaded");
            await query.refetch();
          }}
        />
      </div>

      <div className="space-y-2">
        <p className="text-sm font-medium">Uploaded files</p>
        {query.isLoading && (
          <p className="text-muted-foreground text-sm">Loading…</p>
        )}
        {query.isError && (
          <p className="text-destructive text-sm">Failed to load documents.</p>
        )}
        {!query.isLoading && (query.data?.length ?? 0) === 0 && (
          <p className="text-muted-foreground text-sm">No documents yet.</p>
        )}
        {query.data?.map((doc: OpportunityDocument) => (
          <div
            key={doc.id}
            className="flex items-center justify-between rounded-lg border px-4 py-3"
          >
            <div>
              <p className="text-sm font-medium">
                {TYPE_LABELS[doc.document_type] ?? doc.document_type}
              </p>
              <p className="text-muted-foreground text-xs">
                {new Date(doc.uploaded_at).toLocaleString()}
              </p>
            </div>
            <a
              href={doc.file_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-foreground"
              aria-label="Open document"
            >
              <ExternalLink className="h-4 w-4" />
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
