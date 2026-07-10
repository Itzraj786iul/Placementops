"use client";

import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FileUpload } from "@/components/ui/file-upload";
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
  deleteResume,
  replaceResumeFile,
  updateResume,
  uploadResume,
} from "@/features/student-onboarding/api/student-client";

export function ResumeStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { resumes } = useStudentOnboardingData(profileId);
  const { invalidateAll } = useInvalidateStudentQueries();
  const [showUpload, setShowUpload] = React.useState(false);
  const [name, setName] = React.useState("");
  const [renamingId, setRenamingId] = React.useState<string | null>(null);
  const [renameValue, setRenameValue] = React.useState("");
  const [replacingId, setReplacingId] = React.useState<string | null>(null);

  const refresh = React.useCallback(async () => {
    await invalidateAll(profileId);
  }, [invalidateAll, profileId]);

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
      description="Upload PDF or Word resumes and mark one as active."
    >
      {!resumes.data?.length && !showUpload ? (
        <EmptyState
          title="No resumes yet"
          description="Upload your first resume (PDF, DOC, or DOCX, max 10 MB)."
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
              <div key={resume.id} className="space-y-2">
                <ResumeCard
                  resume={resume}
                  isReadOnly={isReadOnly}
                  onActivate={() => handleActivate(resume.id)}
                  onRename={() => {
                    setRenamingId(resume.id);
                    setRenameValue(resume.name);
                  }}
                  onDelete={() => handleDelete(resume.id)}
                />
                {!isReadOnly && (
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() =>
                      setReplacingId(
                        replacingId === resume.id ? null : resume.id,
                      )
                    }
                  >
                    {replacingId === resume.id
                      ? "Cancel replace"
                      : "Replace file"}
                  </Button>
                )}
                {replacingId === resume.id && (
                  <FileUpload
                    category="resume"
                    hint="PDF, DOC, DOCX · max 10 MB"
                    onUpload={async (file, onProgress) => {
                      await replaceResumeFile(
                        profileId,
                        resume.id,
                        file,
                        onProgress,
                      );
                      toast.success("Resume file replaced");
                      setReplacingId(null);
                      await refresh();
                    }}
                  />
                )}
              </div>
            ),
          )}
        </div>
      )}
      {!isReadOnly && (showUpload || (resumes.data?.length ?? 0) > 0) && (
        <div className="mt-6 space-y-3 rounded-lg border border-dashed p-4">
          <p className="text-sm font-medium">Add resume</p>
          <FormField label="Resume Name (optional)">
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Software Engineering Resume"
            />
          </FormField>
          <FileUpload
            category="resume"
            hint="PDF, DOC, DOCX · max 10 MB"
            onUpload={async (file, onProgress) => {
              const isFirst = !resumes.data?.length;
              await uploadResume(
                profileId,
                file,
                {
                  name: name.trim() || undefined,
                  is_active: isFirst,
                },
                onProgress,
              );
              toast.success("Resume uploaded");
              setName("");
              setShowUpload(false);
              await refresh();
            }}
          />
        </div>
      )}
    </SectionCard>
  );
}
