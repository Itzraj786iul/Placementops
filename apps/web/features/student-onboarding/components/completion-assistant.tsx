"use client";

import {
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  PartyPopper,
} from "lucide-react";

import { Button } from "@/components/ui/button";
import { ProgressCircle } from "@/features/student-onboarding/components/progress-circle";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import type { MissingRequirement } from "@/features/student-onboarding/types";
import { cn } from "@/lib/utils";

type CompletionAssistantProps = {
  className?: string;
  onSubmitReady?: () => void;
};

export function CompletionAssistant({
  className,
  onSubmitReady,
}: CompletionAssistantProps) {
  const { profile, completion, navigateToRequirement, setCurrentStep } =
    useOnboarding();

  const missing = profile.missing_requirements ?? [];
  const completed = profile.requirements_completed ?? 0;
  const total = profile.requirements_total ?? 0;
  const optionalCompleted = profile.optional_completed ?? 0;
  const optionalTotal = profile.optional_total ?? 0;
  const estimated = profile.estimated_minutes_remaining ?? 0;
  const isComplete = completion >= 100 && missing.length === 0;

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
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
            <p className="font-medium">Profile Completion</p>
            <p className="text-muted-foreground">{completion}%</p>
          </div>
          <ProgressCircle value={completion} />
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <div className="rounded-lg border px-4 py-3">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Required Items
          </p>
          <p className="mt-1 text-xl font-semibold">
            {completed} / {total}
          </p>
        </div>
        <div className="rounded-lg border px-4 py-3">
          <p className="text-muted-foreground text-xs tracking-wide uppercase">
            Optional Items
          </p>
          <p className="mt-1 text-xl font-semibold">
            {optionalCompleted} / {optionalTotal}
          </p>
        </div>
      </div>

      {isComplete ? (
        <div
          className="rounded-lg border border-green-200 bg-green-50 px-4 py-4 dark:border-green-900 dark:bg-green-950/40"
          role="status"
        >
          <div className="flex items-start gap-3">
            <PartyPopper className="mt-0.5 h-5 w-5 shrink-0 text-green-700 dark:text-green-300" />
            <div className="space-y-2">
              <p className="font-medium text-green-900 dark:text-green-100">
                Congratulations! Your profile is complete.
              </p>
              <p className="text-muted-foreground text-sm">
                You are ready to apply for placement opportunities. Submit your
                profile for Placement Cell verification.
              </p>
              <Button
                type="button"
                size="sm"
                onClick={() => {
                  setCurrentStep("review");
                  onSubmitReady?.();
                }}
              >
                Go to Submit
              </Button>
            </div>
          </div>
        </div>
      ) : (
        <div className="rounded-lg border border-amber-200 bg-amber-50/80 px-4 py-4 dark:border-amber-900 dark:bg-amber-950/30">
          <div className="flex items-start gap-2">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-700 dark:text-amber-300" />
            <div className="min-w-0 flex-1 space-y-3">
              <div>
                <p className="font-medium text-amber-950 dark:text-amber-100">
                  You&apos;re almost ready!
                </p>
                <p className="text-muted-foreground mt-1 text-sm">
                  {completed} / {total} required items completed. Finish the
                  items below
                  {estimated > 0 ? ` · about ${estimated} min` : ""}.
                </p>
              </div>
              <ul className="space-y-2" aria-label="Missing required items">
                {missing.map((item) => (
                  <MissingAction
                    key={item.code}
                    item={item}
                    onNavigate={navigateToRequirement}
                  />
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function MissingAction({
  item,
  onNavigate,
}: {
  item: MissingRequirement;
  onNavigate: (item: MissingRequirement) => void;
}) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onNavigate(item)}
        className="group hover:bg-background flex w-full items-center justify-between gap-3 rounded-md border bg-white/70 px-3 py-2 text-left text-sm transition-colors dark:bg-black/20"
        aria-label={`${item.label}. Go to ${item.step} step`}
      >
        <span className="flex items-center gap-2">
          <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-600" />
          <span>{item.label}</span>
        </span>
        <ArrowRight className="text-muted-foreground h-4 w-4 shrink-0 transition-transform group-hover:translate-x-0.5" />
      </button>
    </li>
  );
}

export function SectionStatusBadge({
  status,
}: {
  status: "complete" | "incomplete" | "not_started";
}) {
  if (status === "complete") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800 dark:bg-green-950 dark:text-green-300">
        <CheckCircle2 className="h-3 w-3" />
        Complete
      </span>
    );
  }
  if (status === "incomplete") {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-900 dark:bg-amber-950 dark:text-amber-300">
        <AlertTriangle className="h-3 w-3" />
        Incomplete
      </span>
    );
  }
  return (
    <span className="bg-muted text-muted-foreground inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium">
      Not Started
    </span>
  );
}
