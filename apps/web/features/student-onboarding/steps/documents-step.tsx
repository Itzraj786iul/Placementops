"use client";

import * as React from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

import {
  DocumentCard,
  type DocumentUploadPhase,
} from "@/features/student-onboarding/components/document-card";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  DOCUMENT_STEP_TYPES,
  REQUIRED_DOCUMENT_TYPES,
} from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  studentQueryKeys,
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import { uploadDocument } from "@/features/student-onboarding/api/student-client";
import type {
  DocumentType,
  StudentDocument,
} from "@/features/student-onboarding/types";

type UploadState = {
  phase: DocumentUploadPhase;
  progress: number;
};

export function DocumentsStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { documents, verification } = useStudentOnboardingData(profileId);
  const { invalidateProfile } = useInvalidateStudentQueries();
  const queryClient = useQueryClient();
  const [uploadState, setUploadState] = React.useState<
    Partial<Record<DocumentType, UploadState>>
  >({});

  if (documents.isLoading) return <StepSkeleton />;

  const rejectionNote =
    verification.data?.documents_status === "REJECTED"
      ? verification.data.remarks
      : null;

  const requiredSet = new Set<string>(REQUIRED_DOCUMENT_TYPES);
  const docsKey = studentQueryKeys.documents(profileId);

  const handleFileSelected = async (type: DocumentType, file: File) => {
    setUploadState((prev) => ({
      ...prev,
      [type]: { phase: "uploading", progress: 0 },
    }));
    try {
      const uploaded = await uploadDocument(
        profileId,
        file,
        { document_type: type, file_name: file.name },
        (pct) => {
          setUploadState((prev) => ({
            ...prev,
            [type]: { phase: "uploading", progress: pct },
          }));
        },
      );
      setUploadState((prev) => ({
        ...prev,
        [type]: { phase: "processing", progress: 100 },
      }));
      queryClient.setQueryData<StudentDocument[]>(docsKey, (old) => {
        const list = old ?? [];
        const without = list.filter((d) => d.document_type !== type);
        return [...without, uploaded];
      });
      void invalidateProfile();
      toast.success("Document uploaded — pending verification");
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setUploadState((prev) => {
        const next = { ...prev };
        delete next[type];
        return next;
      });
    }
  };

  return (
    <SectionCard
      title="Documents"
      description="Upload Aadhar and marksheets. Profile photo is collected in Personal Information."
      focusId="documents-section"
      status={
        REQUIRED_DOCUMENT_TYPES.every((type) =>
          (documents.data ?? []).some((d) => d.document_type === type),
        )
          ? "complete"
          : (documents.data?.length ?? 0) > 0
            ? "incomplete"
            : "not_started"
      }
    >
      <div className="grid gap-4 sm:grid-cols-2">
        {DOCUMENT_STEP_TYPES.map((type) => {
          const doc = documents.data?.find((d) => d.document_type === type);
          const state = uploadState[type];
          return (
            <DocumentCard
              key={type}
              documentType={type}
              document={doc}
              isReadOnly={isReadOnly}
              rejectionNote={rejectionNote}
              required={requiredSet.has(type)}
              uploadPhase={state?.phase ?? "idle"}
              uploadProgress={state?.progress ?? 0}
              onFileSelected={(file) => {
                void handleFileSelected(type, file);
              }}
            />
          );
        })}
      </div>
      <p className="text-muted-foreground mt-4 text-xs">
        Required: Aadhar, 10th marksheet, and 12th marksheet. Uploaded files
        show as Pending Verification until staff review.
      </p>
    </SectionCard>
  );
}
