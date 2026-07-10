"use client";

import { ExternalLink } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CrmEmptyState } from "@/features/company-crm/components/empty-state";
import { DOCUMENT_LABELS } from "@/features/company-crm/constants";
import type { CompanyDocument } from "@/features/company-crm/types";
import { formatRelativeDate } from "@/features/company-crm/utils/filter-companies";

type DocumentCardProps = {
  document: CompanyDocument;
};

export function DocumentCard({ document }: DocumentCardProps) {
  return (
    <div className="flex items-center justify-between rounded-lg border p-4">
      <div>
        <Badge variant="outline">
          {DOCUMENT_LABELS[document.document_type]}
        </Badge>
        <p className="text-muted-foreground mt-1 text-xs">
          Uploaded {formatRelativeDate(document.uploaded_at)} by{" "}
          {document.uploaded_by.slice(0, 8)}…
        </p>
      </div>
      <a
        href={document.file_url}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary inline-flex items-center gap-1 text-sm"
      >
        Open <ExternalLink className="h-3.5 w-3.5" />
      </a>
    </div>
  );
}

type DocumentsTabProps = {
  documents: CompanyDocument[];
  onUpload: () => void;
};

export function DocumentsTab({ documents, onUpload }: DocumentsTabProps) {
  return (
    <div className="space-y-4 p-4">
      <div className="flex justify-end">
        <Button type="button" size="sm" onClick={onUpload}>
          Upload Document
        </Button>
      </div>
      {documents.length === 0 ? (
        <CrmEmptyState
          title="No documents uploaded"
          description="Upload JDs, eligibility docs, and offer templates. Documents uploaded this session appear here."
          action={
            <Button type="button" size="sm" onClick={onUpload}>
              Upload Document
            </Button>
          }
        />
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <DocumentCard key={doc.id} document={doc} />
          ))}
        </div>
      )}
    </div>
  );
}
