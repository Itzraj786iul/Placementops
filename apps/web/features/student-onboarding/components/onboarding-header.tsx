"use client";

import { ProgressCircle } from "@/features/student-onboarding/components/progress-circle";

type OnboardingHeaderProps = {
  completion: number;
};

export function OnboardingHeader({ completion }: OnboardingHeaderProps) {
  return (
    <div className="flex flex-col gap-4 border-b pb-6 sm:flex-row sm:items-start sm:justify-between">
      <div className="space-y-1">
        <h1 className="text-2xl font-semibold tracking-tight">
          Complete Your Placement Profile
        </h1>
        <p className="text-muted-foreground text-sm">
          Complete your profile once. Use it for every placement drive.
        </p>
      </div>
      <div className="flex items-center gap-3">
        <div className="text-right text-sm">
          <p className="font-medium">Overall Profile Completion</p>
          <p className="text-muted-foreground">Updated automatically</p>
        </div>
        <ProgressCircle value={completion} />
      </div>
    </div>
  );
}
