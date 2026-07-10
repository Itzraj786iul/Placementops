"use client";

import * as React from "react";
import { toast } from "sonner";

import { FileUpload } from "@/components/ui/file-upload";
import { DocumentCard } from "@/features/student-onboarding/components/document-card";
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
import { uploadDocument } from "@/features/student-onboarding/api/student-client";
import type { DocumentType } from "@/features/student-onboarding/types";

const ALL_DOC_TYPES = Object.keys(DOCUMENT_TYPE_LABELS) as DocumentType[];

export function DocumentsStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { documents, verification } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [uploadType, setUploadType] = React.useState<DocumentType | null>(null);

  const refresh = async () => {
    await invalidateAll(profileId);
    setUploadType(null);
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
      description="Upload required verification documents (PDF/DOC/images)."
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
              onUpload={() => setUploadType(type)}
            />
          );
        })}
      </div>
      {uploadType && !isReadOnly && (
        <div className="mt-6 space-y-3 rounded-lg border p-4">
          <p className="text-sm font-medium">
            Upload {DOCUMENT_TYPE_LABELS[uploadType]}
          </p>
          <FileUpload
            category={uploadType === "PHOTO" ? "image" : "document"}
            hint={
              uploadType === "PHOTO"
                ? "PNG, JPG · max 5 MB"
                : "PDF, DOC, DOCX, PNG, JPG · max 10 MB"
            }
            onUpload={async (file, onProgress) => {
              await uploadDocument(
                profileId,
                file,
                {
                  document_type: uploadType,
                  file_name: file.name,
                },
                onProgress,
              );
              toast.success("Document uploaded");
              await refresh();
            }}
          />
        </div>
      )}
    </SectionCard>
  );
}
