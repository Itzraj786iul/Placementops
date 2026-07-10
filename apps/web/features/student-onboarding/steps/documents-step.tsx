"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { DocumentCard } from "@/features/student-onboarding/components/document-card";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  DOCUMENT_TYPE_LABELS,
  REQUIRED_DOCUMENT_TYPES,
} from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import {
  createDocument,
  updateDocument,
} from "@/features/student-onboarding/api/student-client";
import type { DocumentType } from "@/features/student-onboarding/types";

const ALL_DOC_TYPES = Object.keys(DOCUMENT_TYPE_LABELS) as DocumentType[];

export function DocumentsStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { documents, verification } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [uploadType, setUploadType] = React.useState<DocumentType | null>(null);
  const [fileUrl, setFileUrl] = React.useState("");
  const [fileName, setFileName] = React.useState("");

  const refresh = async () => {
    await invalidateAll(profileId);
    setUploadType(null);
    setFileUrl("");
    setFileName("");
  };

  const handleUpload = async () => {
    if (!uploadType || !fileUrl.trim() || !fileName.trim()) return;
    const existing = documents.data?.find(
      (d) => d.document_type === uploadType,
    );
    if (existing) {
      await updateDocument(profileId, existing.id, {
        file_url: fileUrl.trim(),
        file_name: fileName.trim(),
      });
    } else {
      await createDocument(profileId, {
        document_type: uploadType,
        file_url: fileUrl.trim(),
        file_name: fileName.trim(),
      });
    }
    await refresh();
  };

  if (documents.isLoading) return <StepSkeleton />;

  const rejectionNote =
    verification.data?.documents_status === "REJECTED"
      ? verification.data.remarks
      : null;

  const displayTypes = [
    ...REQUIRED_DOCUMENT_TYPES,
    ...ALL_DOC_TYPES.filter(
      (t) =>
        !REQUIRED_DOCUMENT_TYPES.includes(
          t as (typeof REQUIRED_DOCUMENT_TYPES)[number],
        ),
    ),
  ];

  return (
    <SectionCard
      title="Documents"
      description="Upload required verification documents."
    >
      <div className="grid gap-4 sm:grid-cols-2">
        {displayTypes.map((type) => {
          const doc = documents.data?.find((d) => d.document_type === type);
          return (
            <DocumentCard
              key={type}
              documentType={type}
              document={doc}
              isReadOnly={isReadOnly}
              rejectionNote={rejectionNote}
              onUpload={() => {
                setUploadType(type);
                setFileName(doc?.file_name ?? "");
                setFileUrl(doc?.file_url ?? "");
              }}
            />
          );
        })}
      </div>
      {uploadType && !isReadOnly && (
        <div className="mt-6 space-y-3 rounded-lg border p-4">
          <p className="text-sm font-medium">
            Upload {DOCUMENT_TYPE_LABELS[uploadType]}
          </p>
          <FormField label="File Name">
            <Input
              value={fileName}
              onChange={(e) => setFileName(e.target.value)}
            />
          </FormField>
          <FormField label="File URL">
            <Input
              value={fileUrl}
              onChange={(e) => setFileUrl(e.target.value)}
              placeholder="https://..."
            />
          </FormField>
          <div className="flex gap-2">
            <Button type="button" size="sm" onClick={handleUpload}>
              Save Document
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={() => setUploadType(null)}
            >
              Cancel
            </Button>
          </div>
        </div>
      )}
    </SectionCard>
  );
}
