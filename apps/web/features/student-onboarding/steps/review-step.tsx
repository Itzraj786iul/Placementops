"use client";

import * as React from "react";
import { toast } from "sonner";

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
import { submitMyProfile } from "@/features/student-onboarding/api/student-client";
import { getIncompleteSections } from "@/features/student-onboarding/utils/step-status";
import type { VerificationStatus } from "@/features/student-onboarding/types";
import { ApiError } from "@/lib/api-client";

function sectionVerification(
  complete: boolean,
  status: VerificationStatus | null | undefined,
): VerificationStatus | null {
  // Only show verification once the section has content to review.
  if (!complete) return null;
  return status ?? "PENDING";
}

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

  const verification = data.verification.data ?? null;
  const sectionData = {
    personal: data.personal.data ?? null,
    academic: data.academic.data ?? null,
    education: data.education.data ?? [],
    resumes: data.resumes.data ?? [],
    documents: data.documents.data ?? [],
    skills: data.skills.data ?? [],
    projects: data.projects.data ?? [],
    verification,
  };

  const incomplete = getIncompleteSections(sectionData);
  const isSubmittedForReview =
    profile.profile_status === "SUBMITTED" ||
    profile.profile_status === "UNDER_REVIEW";
  const canSubmit =
    canSubmitProfile(completion) &&
    !isReadOnly &&
    (profile.profile_status === "DRAFT" ||
      profile.profile_status === "REJECTED");

  const personalComplete = Boolean(sectionData.personal);
  const academicComplete = Boolean(sectionData.academic);
  const educationComplete = sectionData.education.length > 0;
  const resumeComplete = sectionData.resumes.length > 0;
  const documentsComplete = incomplete.every((s) => s !== "Documents");
  const skillsComplete = sectionData.skills.length > 0;
  const projectsComplete = sectionData.projects.length > 0;

  const handleSubmit = async () => {
    setSubmitError(null);
    setIsSubmitting(true);
    try {
      await submitMyProfile();
      await invalidateProfile();
      toast.success("Profile submitted for review");
    } catch (error) {
      const message =
        error instanceof ApiError
          ? error.message
          : "Unable to submit profile. Please try again.";
      setSubmitError(message);
      toast.error(message);
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

      {isSubmittedForReview && (
        <div
          className="mb-6 rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm dark:border-blue-900 dark:bg-blue-950/40"
          role="status"
        >
          <p className="font-medium text-blue-900 dark:text-blue-100">
            Submitted for review
          </p>
          <p className="text-muted-foreground mt-1">
            Your profile is with the Placement Cell / Convener. You will be able
            to edit again if it is rejected.
          </p>
        </div>
      )}

      {profile.profile_status === "REJECTED" && verification?.remarks && (
        <div className="border-destructive/30 bg-destructive/5 mb-6 rounded-lg border p-4 text-sm">
          <p className="text-destructive font-medium">Reviewer feedback</p>
          <p className="text-muted-foreground mt-1">{verification.remarks}</p>
        </div>
      )}

      <div className="grid gap-4">
        <ReviewCard
          title="Personal Information"
          complete={personalComplete}
          verificationStatus={sectionVerification(
            personalComplete,
            verification?.personal_status,
          )}
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
          complete={academicComplete}
          verificationStatus={sectionVerification(
            academicComplete,
            verification?.academic_status,
          )}
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
          complete={educationComplete}
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
          complete={resumeComplete}
          verificationStatus={sectionVerification(
            resumeComplete,
            verification?.resume_status,
          )}
          onEdit={() => setCurrentStep("resume")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.resumes.length} resume(s)
          </p>
        </ReviewCard>
        <ReviewCard
          title="Documents"
          complete={documentsComplete}
          verificationStatus={sectionVerification(
            documentsComplete,
            verification?.documents_status,
          )}
          onEdit={() => setCurrentStep("documents")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.documents.length} document(s) uploaded
          </p>
        </ReviewCard>
        <ReviewCard
          title="Skills"
          complete={skillsComplete}
          onEdit={() => setCurrentStep("skills")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.skills.map((s) => s.skill_name).join(", ") || "None"}
          </p>
        </ReviewCard>
        <ReviewCard
          title="Projects"
          complete={projectsComplete}
          onEdit={() => setCurrentStep("projects")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.projects.map((p) => p.title).join(", ") || "None"}
          </p>
        </ReviewCard>
      </div>

      <div className="mt-8 rounded-lg border p-4">
        {isSubmittedForReview ? null : isProfileReadOnly(
            profile.profile_status,
          ) ? (
          <p className="text-muted-foreground text-sm">
            Your profile is verified and read-only.
          </p>
        ) : canSubmit ? (
          <div className="space-y-3">
            <div className="space-y-2 text-sm">
              <p className="font-medium">Your profile is complete.</p>
              <p className="text-muted-foreground">
                After submission, the Placement Cell will review your
                information and documents. You will be notified once
                verification is complete.
              </p>
            </div>
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
            {!canSubmitProfile(completion) ? (
              <>
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
              </>
            ) : (
              <p className="text-muted-foreground text-sm">
                Only draft or rejected profiles can be submitted for review.
                Current status: {profile.profile_status}.
              </p>
            )}
            {submitError && (
              <p className="text-destructive text-sm" role="alert">
                {submitError}
              </p>
            )}
          </div>
        )}
      </div>
    </SectionCard>
  );
}
