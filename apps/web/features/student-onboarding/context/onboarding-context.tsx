"use client";

import * as React from "react";

import type { OnboardingStepId } from "@/features/student-onboarding/constants";
import type {
  MissingRequirement,
  StudentProfile,
} from "@/features/student-onboarding/types";

type OnboardingContextValue = {
  profile: StudentProfile;
  profileId: string;
  isReadOnly: boolean;
  currentStep: OnboardingStepId;
  setCurrentStep: (step: OnboardingStepId) => void;
  completion: number;
  focusTarget: string | null;
  navigateToRequirement: (item: MissingRequirement) => void;
  clearFocusTarget: () => void;
};

const OnboardingContext = React.createContext<OnboardingContextValue | null>(
  null,
);

const VALID_STEPS = new Set<OnboardingStepId>([
  "personal",
  "academic",
  "education",
  "resume",
  "documents",
  "skills",
  "projects",
  "review",
]);

export function OnboardingProvider({
  profile,
  isReadOnly,
  currentStep,
  setCurrentStep,
  completion,
  children,
}: {
  profile: StudentProfile;
  isReadOnly: boolean;
  currentStep: OnboardingStepId;
  setCurrentStep: (step: OnboardingStepId) => void;
  completion: number;
  children: React.ReactNode;
}) {
  const [focusTarget, setFocusTarget] = React.useState<string | null>(null);

  const clearFocusTarget = React.useCallback(() => {
    setFocusTarget(null);
  }, []);

  const navigateToRequirement = React.useCallback(
    (item: MissingRequirement) => {
      const step = item.step as OnboardingStepId;
      if (!VALID_STEPS.has(step) || step === "review") return;
      setFocusTarget(item.focus ?? null);
      setCurrentStep(step);
    },
    [setCurrentStep],
  );

  const value = React.useMemo(
    () => ({
      profile,
      profileId: profile.id,
      isReadOnly,
      currentStep,
      setCurrentStep,
      completion,
      focusTarget,
      navigateToRequirement,
      clearFocusTarget,
    }),
    [
      profile,
      isReadOnly,
      currentStep,
      setCurrentStep,
      completion,
      focusTarget,
      navigateToRequirement,
      clearFocusTarget,
    ],
  );

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const context = React.useContext(OnboardingContext);
  if (!context) {
    throw new Error("useOnboarding must be used within OnboardingProvider");
  }
  return context;
}
