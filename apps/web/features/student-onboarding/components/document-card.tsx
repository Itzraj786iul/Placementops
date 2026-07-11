"use client";

import { ExternalLink, Loader2, Upload } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/features/student-onboarding/components/status-badge";
import { DOCUMENT_TYPE_LABELS } from "@/features/student-onboarding/constants";
import type {
  DocumentType,
  StudentDocument,
} from "@/features/student-onboarding/types";

const ACCEPT_BY_TYPE: Record<DocumentType, string> = {
  PHOTO: ".png,.jpg,.jpeg,image/png,image/jpeg",
  AADHAR: ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
  PAN: ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
  TENTH_MARKSHEET: ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
  TWELFTH_MARKSHEET:
    ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
  SEMESTER_MARKSHEET:
    ".pdf,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
  RESUME: ".pdf,.doc,.docx,application/pdf",
  OTHER: ".pdf,.doc,.docx,.png,.jpg,.jpeg,application/pdf,image/png,image/jpeg",
};

type DocumentCardProps = {
  documentType: DocumentType;
  document?: StudentDocument;
  isReadOnly: boolean;
  rejectionNote?: string | null;
  isUploading?: boolean;
  onFileSelected: (file: File) => void;
};

export function DocumentCard({
  documentType,
  document,
  isReadOnly,
  rejectionNote,
  isUploading = false,
  onFileSelected,
}: DocumentCardProps) {
  const inputRef = React.useRef<HTMLInputElement>(null);
  const label = DOCUMENT_TYPE_LABELS[documentType] ?? documentType;
  const status = document?.status ?? "PENDING";

  const openPicker = () => {
    if (isReadOnly || isUploading) return;
    inputRef.current?.click();
  };

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
        <>
          <input
            ref={inputRef}
            type="file"
            className="sr-only"
            accept={ACCEPT_BY_TYPE[documentType]}
            disabled={isUploading}
            onChange={(event) => {
              const file = event.target.files?.[0];
              // Allow selecting the same file again after a failed upload.
              event.target.value = "";
              if (file) onFileSelected(file);
            }}
          />
          <Button
            type="button"
            size="sm"
            variant="outline"
            className="mt-4"
            disabled={isUploading}
            onClick={openPicker}
          >
            {isUploading ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Upload className="h-3.5 w-3.5" />
            )}
            {isUploading ? "Uploading…" : document ? "Replace" : "Upload"}
          </Button>
        </>
      )}
    </div>
  );
}
