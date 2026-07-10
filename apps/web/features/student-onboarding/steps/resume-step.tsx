"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/features/student-onboarding/components/empty-state";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { ResumeCard } from "@/features/student-onboarding/components/resume-card";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import {
  createResume,
  deleteResume,
  updateResume,
} from "@/features/student-onboarding/api/student-client";

export function ResumeStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { resumes } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [showUpload, setShowUpload] = React.useState(false);
  const [name, setName] = React.useState("");
  const [fileUrl, setFileUrl] = React.useState("");
  const [renamingId, setRenamingId] = React.useState<string | null>(null);
  const [renameValue, setRenameValue] = React.useState("");

  const refresh = React.useCallback(async () => {
    await invalidateAll(profileId);
  }, [invalidateAll, profileId]);

  const handleUpload = async () => {
    if (!name.trim() || !fileUrl.trim()) return;
    const isFirst = !resumes.data?.length;
    await createResume(profileId, {
      name: name.trim(),
      file_url: fileUrl.trim(),
      version: 1,
      is_active: isFirst,
    });
    setName("");
    setFileUrl("");
    setShowUpload(false);
    await refresh();
  };

  const handleActivate = async (resumeId: string) => {
    const all = resumes.data ?? [];
    await Promise.all(
      all.map((r) =>
        updateResume(profileId, r.id, { is_active: r.id === resumeId }),
      ),
    );
    await refresh();
  };

  const handleRename = async (resumeId: string) => {
    if (!renameValue.trim()) return;
    await updateResume(profileId, resumeId, { name: renameValue.trim() });
    setRenamingId(null);
    setRenameValue("");
    await refresh();
  };

  const handleDelete = async (resumeId: string) => {
    await deleteResume(profileId, resumeId);
    await refresh();
  };

  if (resumes.isLoading) return <StepSkeleton />;

  return (
    <SectionCard
      title="Resume Library"
      description="Upload multiple resumes and mark one as active."
    >
      {!resumes.data?.length && !showUpload ? (
        <EmptyState
          title="No resumes yet"
          description="Upload your first resume using a shareable file link."
          action={
            !isReadOnly && (
              <Button type="button" onClick={() => setShowUpload(true)}>
                Upload Resume
              </Button>
            )
          }
        />
      ) : (
        <div className="space-y-4">
          {resumes.data?.map((resume) =>
            renamingId === resume.id ? (
              <div key={resume.id} className="flex gap-2">
                <Input
                  value={renameValue}
                  onChange={(e) => setRenameValue(e.target.value)}
                  placeholder="Resume name"
                />
                <Button
                  type="button"
                  size="sm"
                  onClick={() => handleRename(resume.id)}
                >
                  Save
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  onClick={() => setRenamingId(null)}
                >
                  Cancel
                </Button>
              </div>
            ) : (
              <ResumeCard
                key={resume.id}
                resume={resume}
                isReadOnly={isReadOnly}
                onActivate={() => handleActivate(resume.id)}
                onRename={() => {
                  setRenamingId(resume.id);
                  setRenameValue(resume.name);
                }}
                onDelete={() => handleDelete(resume.id)}
              />
            ),
          )}
        </div>
      )}
      {!isReadOnly && (showUpload || (resumes.data?.length ?? 0) > 0) && (
        <div className="mt-6 space-y-3 rounded-lg border border-dashed p-4">
          <p className="text-sm font-medium">Add resume</p>
          <FormField label="Resume Name">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Software Engineering Resume"
            />
          </FormField>
          <FormField label="File URL">
            <Input
              value={fileUrl}
              onChange={(e) => setFileUrl(e.target.value)}
              placeholder="https://..."
            />
          </FormField>
          <Button type="button" size="sm" onClick={handleUpload}>
            Upload
          </Button>
        </div>
      )}
    </SectionCard>
  );
}
