"use client";

import * as React from "react";
import { toast } from "sonner";

import { DocumentCard } from "@/features/student-onboarding/components/document-card";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import { DOCUMENT_STEP_TYPES } from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import { uploadDocument } from "@/features/student-onboarding/api/student-client";
import type { DocumentType } from "@/features/student-onboarding/types";

export function DocumentsStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { documents, verification } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [uploadingType, setUploadingType] = React.useState<DocumentType | null>(
    null,
  );

  if (documents.isLoading) return <StepSkeleton />;

  const rejectionNote =
    verification.data?.documents_status === "REJECTED"
      ? verification.data.remarks
      : null;

  const handleFileSelected = async (type: DocumentType, file: File) => {
    setUploadingType(type);
    try {
      await uploadDocument(profileId, file, {
        document_type: type,
        file_name: file.name,
      });
      toast.success("Document uploaded");
      await invalidateAll(profileId);
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploadingType(null);
    }
  };

  return (
    <SectionCard
      title="Documents"
      description="Upload Aadhar and marksheets. Profile photo is collected in Personal Information."
    >
      <div className="grid gap-4 sm:grid-cols-2">
        {DOCUMENT_STEP_TYPES.map((type) => {
          const doc = documents.data?.find((d) => d.document_type === type);
          return (
            <DocumentCard
              key={type}
              documentType={type}
              document={doc}
              isReadOnly={isReadOnly}
              rejectionNote={rejectionNote}
              isUploading={uploadingType === type}
              onFileSelected={(file) => {
                void handleFileSelected(type, file);
              }}
            />
          );
        })}
      </div>
      <p className="text-muted-foreground mt-4 text-xs">
        Required: Aadhar, 10th marksheet, and 12th marksheet.
      </p>
    </SectionCard>
  );
}
