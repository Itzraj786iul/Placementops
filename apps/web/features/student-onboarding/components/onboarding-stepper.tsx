"use client";

import { AlertTriangle, Check, Lock } from "lucide-react";

import type { OnboardingStepId } from "@/features/student-onboarding/constants";
import { cn } from "@/lib/utils";

export type StepState =
  | "completed"
  | "current"
  | "locked"
  | "rejected"
  | "incomplete"
  | "not_started";

export type StepperItem = {
  id: OnboardingStepId;
  label: string;
  state: StepState;
};

type OnboardingStepperProps = {
  steps: StepperItem[];
  currentStep: OnboardingStepId;
  onStepSelect: (step: OnboardingStepId) => void;
};

function statusLabel(state: StepState): string {
  if (state === "completed") return "Complete";
  if (state === "rejected") return "Needs attention";
  if (state === "incomplete") return "Incomplete";
  if (state === "not_started") return "Not Started";
  if (state === "locked") return "Locked";
  return "In progress";
}

export function OnboardingStepper({
  steps,
  currentStep,
  onStepSelect,
}: OnboardingStepperProps) {
  return (
    <nav aria-label="Onboarding progress" className="space-y-1">
      {steps.map((step, index) => {
        const isClickable = step.state !== "locked";
        return (
          <button
            key={step.id}
            type="button"
            disabled={!isClickable}
            onClick={() => isClickable && onStepSelect(step.id)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm transition-colors",
              step.id === currentStep && "bg-accent text-accent-foreground",
              isClickable && step.id !== currentStep && "hover:bg-muted/60",
              !isClickable && "cursor-not-allowed opacity-50",
            )}
            aria-current={step.id === currentStep ? "step" : undefined}
          >
            <StepIcon state={step.state} index={index + 1} />
            <span className="min-w-0 flex-1">
              <span className="block font-medium">{step.label}</span>
              <span className="text-muted-foreground block text-xs">
                {statusLabel(step.state)}
              </span>
            </span>
          </button>
        );
      })}
    </nav>
  );
}

function StepIcon({ state, index }: { state: StepState; index: number }) {
  if (state === "completed") {
    return (
      <span className="bg-primary text-primary-foreground flex h-6 w-6 items-center justify-center rounded-full">
        <Check className="h-3.5 w-3.5" />
      </span>
    );
  }
  if (state === "locked") {
    return (
      <span className="text-muted-foreground flex h-6 w-6 items-center justify-center rounded-full border">
        <Lock className="h-3 w-3" />
      </span>
    );
  }
  if (state === "rejected" || state === "incomplete") {
    return (
      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-amber-500 text-white">
        <AlertTriangle className="h-3 w-3" />
      </span>
    );
  }
  return (
    <span className="border-primary text-primary flex h-6 w-6 items-center justify-center rounded-full border-2 text-xs font-semibold">
      {index}
    </span>
  );
}
