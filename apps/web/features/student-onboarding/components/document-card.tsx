"use client";

import { ExternalLink, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/features/student-onboarding/components/status-badge";
import { DOCUMENT_TYPE_LABELS } from "@/features/student-onboarding/constants";
import type {
  DocumentType,
  StudentDocument,
} from "@/features/student-onboarding/types";

type DocumentCardProps = {
  documentType: DocumentType;
  document?: StudentDocument;
  isReadOnly: boolean;
  rejectionNote?: string | null;
  onUpload: () => void;
};

export function DocumentCard({
  documentType,
  document,
  isReadOnly,
  rejectionNote,
  onUpload,
}: DocumentCardProps) {
  const label = DOCUMENT_TYPE_LABELS[documentType] ?? documentType;
  const status = document?.status ?? "PENDING";

  return (
    <div className="rounded-lg border p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h4 className="font-medium">{label}</h4>
            <StatusBadge status={document ? status : "PENDING"} />
          </div>
          {document ? (
            <p className="text-muted-foreground text-xs">
              {document.file_name} ·{" "}
              {new Date(document.uploaded_at).toLocaleDateString()}
            </p>
          ) : (
            <p className="text-muted-foreground text-sm">Not uploaded yet</p>
          )}
          {status === "REJECTED" && rejectionNote && (
            <p className="text-destructive text-xs">{rejectionNote}</p>
          )}
        </div>
        {document && (
          <a
            href={document.file_url}
            target="_blank"
            rel="noopener noreferrer"
            aria-label={`View ${label}`}
          >
            <ExternalLink className="text-muted-foreground h-4 w-4" />
          </a>
        )}
      </div>
      {!isReadOnly && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          className="mt-4"
          onClick={onUpload}
        >
          <Upload className="h-3.5 w-3.5" />
          {document ? "Replace" : "Upload"}
        </Button>
      )}
    </div>
  );
}
