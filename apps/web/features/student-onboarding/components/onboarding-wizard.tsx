"use client";

import * as React from "react";

import {
  OnboardingStepper,
  type StepperItem,
} from "@/features/student-onboarding/components/onboarding-stepper";
import { OnboardingHeader } from "@/features/student-onboarding/components/onboarding-header";
import { ProfileBootstrap } from "@/features/student-onboarding/components/profile-bootstrap";
import { StepNav } from "@/features/student-onboarding/components/step-nav";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  ONBOARDING_STEPS,
  type OnboardingStepId,
  isProfileReadOnly,
} from "@/features/student-onboarding/constants";
import {
  OnboardingProvider,
  useOnboarding,
} from "@/features/student-onboarding/context/onboarding-context";
import {
  useStudentOnboardingData,
  useStudentProfile,
} from "@/features/student-onboarding/hooks/use-student-data";
import { AcademicStep } from "@/features/student-onboarding/steps/academic-step";
import { DocumentsStep } from "@/features/student-onboarding/steps/documents-step";
import { EducationStep } from "@/features/student-onboarding/steps/education-step";
import { PersonalStep } from "@/features/student-onboarding/steps/personal-step";
import { ProjectsStep } from "@/features/student-onboarding/steps/projects-step";
import { ResumeStep } from "@/features/student-onboarding/steps/resume-step";
import { ReviewStep } from "@/features/student-onboarding/steps/review-step";
import { SkillsStep } from "@/features/student-onboarding/steps/skills-step";
import { buildStepperItems } from "@/features/student-onboarding/utils/step-status";
import { ApiError } from "@/lib/api-client";

const STEP_COMPONENTS: Record<OnboardingStepId, React.ComponentType> = {
  personal: PersonalStep,
  academic: AcademicStep,
  education: EducationStep,
  resume: ResumeStep,
  documents: DocumentsStep,
  skills: SkillsStep,
  projects: ProjectsStep,
  review: ReviewStep,
};

export function OnboardingWizard() {
  const profileQuery = useStudentProfile();
  const [currentStep, setCurrentStep] =
    React.useState<OnboardingStepId>("personal");

  if (profileQuery.isLoading) {
    return (
      <div className="space-y-6">
        <StepSkeleton />
      </div>
    );
  }

  const isNotFound =
    profileQuery.isError &&
    profileQuery.error instanceof ApiError &&
    profileQuery.error.statusCode === 404;

  if (isNotFound) {
    return <ProfileBootstrap onCreated={() => profileQuery.refetch()} />;
  }

  if (profileQuery.isError || !profileQuery.data) {
    return (
      <p className="text-destructive text-sm">
        Unable to load your profile. Please refresh the page.
      </p>
    );
  }

  const profile = profileQuery.data;
  const isReadOnly = isProfileReadOnly(profile.profile_status);

  return (
    <OnboardingProvider
      profile={profile}
      isReadOnly={isReadOnly}
      currentStep={currentStep}
      setCurrentStep={setCurrentStep}
      completion={profile.profile_completion}
    >
      <OnboardingLayout
        currentStep={currentStep}
        setCurrentStep={setCurrentStep}
      />
    </OnboardingProvider>
  );
}

function OnboardingLayout({
  currentStep,
  setCurrentStep,
}: {
  currentStep: OnboardingStepId;
  setCurrentStep: (step: OnboardingStepId) => void;
}) {
  const { profileId, completion } = useOnboarding();
  const data = useStudentOnboardingData(profileId);

  const sectionData = React.useMemo(
    () => ({
      personal: data.personal.data ?? null,
      academic: data.academic.data ?? null,
      education: data.education.data ?? [],
      resumes: data.resumes.data ?? [],
      documents: data.documents.data ?? [],
      skills: data.skills.data ?? [],
      projects: data.projects.data ?? [],
      verification: data.verification.data ?? null,
    }),
    [data],
  );

  const stepperItems: StepperItem[] = buildStepperItems(
    currentStep,
    sectionData,
  );
  const StepComponent = STEP_COMPONENTS[currentStep];

  const goToStep = (step: OnboardingStepId) => {
    const item = stepperItems.find((s) => s.id === step);
    if (item?.state === "locked") return;
    setCurrentStep(step);
  };

  const currentIndex = ONBOARDING_STEPS.findIndex((s) => s.id === currentStep);

  return (
    <div className="space-y-8">
      <OnboardingHeader completion={completion} />
      <div className="grid gap-8 lg:grid-cols-[240px_1fr]">
        <aside className="lg:sticky lg:top-6 lg:self-start">
          <OnboardingStepper
            steps={stepperItems}
            currentStep={currentStep}
            onStepSelect={goToStep}
          />
        </aside>
        <main className="min-w-0 space-y-6">
          <StepComponent />
          {currentStep !== "review" && (
            <StepNav
              currentStep={currentStep}
              onPrevious={() => {
                const prev = ONBOARDING_STEPS[currentIndex - 1];
                if (prev) setCurrentStep(prev.id);
              }}
              onNext={() => {
                const next = ONBOARDING_STEPS[currentIndex + 1];
                if (next) setCurrentStep(next.id);
              }}
            />
          )}
        </main>
      </div>
    </div>
  );
}
