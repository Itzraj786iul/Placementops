"use client";

import * as React from "react";

import { Button } from "@/components/ui/button";
import { ReviewCard } from "@/features/student-onboarding/components/review-card";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StatusBadge } from "@/features/student-onboarding/components/status-badge";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  canSubmitProfile,
  EDUCATION_TYPE_LABELS,
  isProfileReadOnly,
} from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import { updateProfile } from "@/features/student-onboarding/api/student-client";
import { getIncompleteSections } from "@/features/student-onboarding/utils/step-status";
import { ApiError } from "@/lib/api-client";

export function ReviewStep() {
  const { profile, profileId, isReadOnly, setCurrentStep, completion } =
    useOnboarding();
  const data = useStudentOnboardingData(profileId);
  const { invalidateProfile } = useInvalidateStudentQueries();
  const [submitError, setSubmitError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  if (data.personal.isLoading || data.academic.isLoading) {
    return <StepSkeleton />;
  }

  const sectionData = {
    personal: data.personal.data ?? null,
    academic: data.academic.data ?? null,
    education: data.education.data ?? [],
    resumes: data.resumes.data ?? [],
    documents: data.documents.data ?? [],
    skills: data.skills.data ?? [],
    projects: data.projects.data ?? [],
    verification: data.verification.data ?? null,
  };

  const incomplete = getIncompleteSections(sectionData);
  const canSubmit = canSubmitProfile(completion) && !isReadOnly;

  const handleSubmit = async () => {
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await updateProfile(profileId, { profile_status: "SUBMITTED" });
      await invalidateProfile();
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to submit profile. Please try again.";
      setSubmitError(message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <SectionCard
      title="Review & Submit"
      description="Review your profile before final submission."
    >
      <div className="mb-6 flex items-center gap-3">
        <span className="text-muted-foreground text-sm">Profile status</span>
        <StatusBadge status={profile.profile_status} />
      </div>

      {profile.profile_status === "REJECTED" &&
        data.verification.data?.remarks && (
          <div className="border-destructive/30 bg-destructive/5 mb-6 rounded-lg border p-4 text-sm">
            <p className="text-destructive font-medium">Reviewer feedback</p>
            <p className="text-muted-foreground mt-1">
              {data.verification.data.remarks}
            </p>
          </div>
        )}

      <div className="grid gap-4">
        <ReviewCard
          title="Personal Information"
          complete={Boolean(sectionData.personal)}
          onEdit={() => setCurrentStep("personal")}
        >
          {sectionData.personal && (
            <p className="text-muted-foreground text-sm">
              {sectionData.personal.first_name} {sectionData.personal.last_name}{" "}
              · {sectionData.personal.phone_number}
            </p>
          )}
        </ReviewCard>
        <ReviewCard
          title="Academic Information"
          complete={Boolean(sectionData.academic)}
          onEdit={() => setCurrentStep("academic")}
        >
          {sectionData.academic && (
            <p className="text-muted-foreground text-sm">
              CGPA {sectionData.academic.current_cgpa} · Semester{" "}
              {sectionData.academic.semester}
            </p>
          )}
        </ReviewCard>
        <ReviewCard
          title="Education History"
          complete={sectionData.education.length > 0}
          onEdit={() => setCurrentStep("education")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.education.length} record(s) ·{" "}
            {sectionData.education
              .map((e) => EDUCATION_TYPE_LABELS[e.education_type])
              .join(", ") || "None"}
          </p>
        </ReviewCard>
        <ReviewCard
          title="Resume Library"
          complete={sectionData.resumes.length > 0}
          onEdit={() => setCurrentStep("resume")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.resumes.length} resume(s)
          </p>
        </ReviewCard>
        <ReviewCard
          title="Documents"
          complete={incomplete.every((s) => s !== "Documents")}
          onEdit={() => setCurrentStep("documents")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.documents.length} document(s) uploaded
          </p>
        </ReviewCard>
        <ReviewCard
          title="Skills"
          complete={sectionData.skills.length > 0}
          onEdit={() => setCurrentStep("skills")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.skills.map((s) => s.skill_name).join(", ") || "None"}
          </p>
        </ReviewCard>
        <ReviewCard
          title="Projects"
          complete={sectionData.projects.length > 0}
          onEdit={() => setCurrentStep("projects")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.projects.map((p) => p.title).join(", ") || "None"}
          </p>
        </ReviewCard>
      </div>

      <div className="mt-8 rounded-lg border p-4">
        {isProfileReadOnly(profile.profile_status) ? (
          <p className="text-muted-foreground text-sm">
            Your profile has been submitted and is now read-only. You will be
            able to edit again if it is rejected by the convener.
          </p>
        ) : canSubmit ? (
          <div className="space-y-3">
            <p className="text-muted-foreground text-sm">
              Your profile is complete. Submit it for placement cell review.
            </p>
            <Button
              type="button"
              onClick={handleSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? "Submitting..." : "Submit Profile"}
            </Button>
            {submitError && (
              <p className="text-destructive text-sm" role="alert">
                {submitError}
              </p>
            )}
          </div>
        ) : (
          <div className="space-y-2">
            <p className="text-sm font-medium">Submission blocked</p>
            <p className="text-muted-foreground text-sm">
              Complete all sections before submitting. Profile completion is{" "}
              {completion}%.
            </p>
            {incomplete.length > 0 && (
              <ul className="text-muted-foreground list-inside list-disc text-sm">
                {incomplete.map((section) => (
                  <li key={section}>{section}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </div>
    </SectionCard>
  );
}
