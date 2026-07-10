"use client";

import { Button } from "@/components/ui/button";
import type { OnboardingStepId } from "@/features/student-onboarding/constants";
import { ONBOARDING_STEPS } from "@/features/student-onboarding/constants";

type StepNavProps = {
  currentStep: OnboardingStepId;
  onPrevious: () => void;
  onNext: () => void;
};

export function StepNav({ currentStep, onPrevious, onNext }: StepNavProps) {
  const index = ONBOARDING_STEPS.findIndex((s) => s.id === currentStep);
  const isFirst = index === 0;
  const isLast = index === ONBOARDING_STEPS.length - 1;

  return (
    <div className="flex justify-between border-t pt-6">
      <Button
        type="button"
        variant="outline"
        onClick={onPrevious}
        disabled={isFirst}
      >
        Previous
      </Button>
      {!isLast && (
        <Button type="button" onClick={onNext}>
          Continue
        </Button>
      )}
    </div>
  );
}
