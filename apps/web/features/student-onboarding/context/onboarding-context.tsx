"use client";

import * as React from "react";

import type { OnboardingStepId } from "@/features/student-onboarding/constants";
import type { StudentProfile } from "@/features/student-onboarding/types";

type OnboardingContextValue = {
  profile: StudentProfile;
  profileId: string;
  isReadOnly: boolean;
  currentStep: OnboardingStepId;
  setCurrentStep: (step: OnboardingStepId) => void;
  completion: number;
};

const OnboardingContext = React.createContext<OnboardingContextValue | null>(
  null,
);

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
  const value = React.useMemo(
    () => ({
      profile,
      profileId: profile.id,
      isReadOnly,
      currentStep,
      setCurrentStep,
      completion,
    }),
    [profile, isReadOnly, currentStep, setCurrentStep, completion],
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
