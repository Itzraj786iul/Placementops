"use client";

import * as React from "react";
import { toast } from "sonner";
import { AlertTriangle, CheckCircle2, PartyPopper } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ReviewCard } from "@/features/student-onboarding/components/review-card";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StatusBadge } from "@/features/student-onboarding/components/status-badge";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  canSubmitProfile,
  EDUCATION_TYPE_LABELS,
  isProfileReadOnly,
  ONBOARDING_STEPS,
  type OnboardingStepId,
} from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import { submitMyProfile } from "@/features/student-onboarding/api/student-client";
import {
  getSectionStatus,
  missingForStep,
} from "@/features/student-onboarding/utils/step-status";
import type { VerificationStatus } from "@/features/student-onboarding/types";
import { ApiError } from "@/lib/api-client";

function sectionVerification(
  complete: boolean,
  status: VerificationStatus | null | undefined,
): VerificationStatus | null {
  if (!complete) return null;
  return status ?? "PENDING";
}

const REVIEW_SECTIONS: {
  id: OnboardingStepId;
  title: string;
}[] = ONBOARDING_STEPS.filter((s) => s.id !== "review").map((s) => ({
  id: s.id,
  title: s.label,
}));

export function ReviewStep() {
  const {
    profile,
    profileId,
    isReadOnly,
    setCurrentStep,
    completion,
    navigateToRequirement,
  } = useOnboarding();
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

  const missing = profile.missing_requirements ?? [];
  const completed = profile.requirements_completed ?? 0;
  const total = profile.requirements_total ?? 0;
  const isSubmittedForReview =
    profile.profile_status === "SUBMITTED" ||
    profile.profile_status === "UNDER_REVIEW";
  const canSubmit =
    canSubmitProfile(completion) &&
    !isReadOnly &&
    (profile.profile_status === "DRAFT" ||
      profile.profile_status === "REJECTED");

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
      status={
        completion >= 100
          ? "complete"
          : missing.length > 0
            ? "incomplete"
            : "not_started"
      }
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

      <div className="mb-6 rounded-lg border p-4">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-muted-foreground text-xs tracking-wide uppercase">
              Profile Complete
            </p>
            <p className="mt-1 text-3xl font-semibold">
              {completed} / {total}
            </p>
            <p className="text-muted-foreground mt-1 text-sm">
              {completion}% overall
            </p>
          </div>
        </div>

        <ul className="mt-4 space-y-2" aria-label="Section checklist">
          {REVIEW_SECTIONS.map((section) => {
            const status = getSectionStatus(section.id, sectionData);
            const gaps = missingForStep(section.id, missing);
            return (
              <li
                key={section.id}
                className="flex flex-col gap-1 rounded-md border px-3 py-2 sm:flex-row sm:items-start sm:justify-between"
              >
                <div className="space-y-1">
                  <p className="flex items-center gap-2 text-sm font-medium">
                    {status === "complete" ? (
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-amber-600" />
                    )}
                    {section.title}
                  </p>
                  {gaps.length > 0 && (
                    <p className="text-muted-foreground text-xs">
                      Missing: {gaps.join(", ")}
                    </p>
                  )}
                </div>
                {status !== "complete" && (
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      const first = missing.find((m) => m.step === section.id);
                      if (first) navigateToRequirement(first);
                      else setCurrentStep(section.id);
                    }}
                  >
                    Fix
                  </Button>
                )}
              </li>
            );
          })}
        </ul>
      </div>

      <div className="grid gap-4">
        <ReviewCard
          title="Personal Information"
          complete={getSectionStatus("personal", sectionData) === "complete"}
          verificationStatus={sectionVerification(
            Boolean(sectionData.personal),
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
          complete={getSectionStatus("academic", sectionData) === "complete"}
          verificationStatus={sectionVerification(
            Boolean(sectionData.academic),
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
          complete={getSectionStatus("education", sectionData) === "complete"}
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
          complete={getSectionStatus("resume", sectionData) === "complete"}
          verificationStatus={sectionVerification(
            sectionData.resumes.length > 0,
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
          complete={getSectionStatus("documents", sectionData) === "complete"}
          verificationStatus={sectionVerification(
            getSectionStatus("documents", sectionData) === "complete",
            verification?.documents_status,
          )}
          onEdit={() => setCurrentStep("documents")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.documents.length} document(s) uploaded
            {missingForStep("documents", missing).length > 0
              ? ` · Missing: ${missingForStep("documents", missing).join(", ")}`
              : ""}
          </p>
        </ReviewCard>
        <ReviewCard
          title="Skills"
          complete={getSectionStatus("skills", sectionData) === "complete"}
          onEdit={() => setCurrentStep("skills")}
        >
          <p className="text-muted-foreground text-sm">
            {sectionData.skills.map((s) => s.skill_name).join(", ") || "None"}
          </p>
        </ReviewCard>
        <ReviewCard
          title="Projects"
          complete={getSectionStatus("projects", sectionData) === "complete"}
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
            <div className="flex items-start gap-3">
              <PartyPopper className="mt-0.5 h-5 w-5 shrink-0 text-green-700" />
              <div className="space-y-2 text-sm">
                <p className="font-medium">
                  Congratulations! Your profile is complete.
                </p>
                <p className="text-muted-foreground">
                  You are ready to apply for placement opportunities. Click
                  below to submit your profile for Placement Cell verification.
                </p>
              </div>
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
          <div className="space-y-3">
            <p className="text-sm font-medium">Submission blocked</p>
            {!canSubmitProfile(completion) ? (
              <>
                <p className="text-muted-foreground text-sm">
                  Finish the remaining required items ({completed}/{total}).
                </p>
                <ul className="space-y-2">
                  {missing.map((item) => (
                    <li key={item.code}>
                      <button
                        type="button"
                        className="text-primary text-sm underline-offset-2 hover:underline"
                        onClick={() => navigateToRequirement(item)}
                      >
                        {item.label}
                      </button>
                    </li>
                  ))}
                </ul>
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
