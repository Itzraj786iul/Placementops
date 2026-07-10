"use client";

import { AlertCircle, Check, CloudOff, Loader2 } from "lucide-react";

import {
  type AutosaveStatus,
  getAutosaveMessage,
} from "@/features/student-onboarding/hooks/use-autosave";
import { cn } from "@/lib/utils";

type AutosaveIndicatorProps = {
  status: AutosaveStatus;
  onRetry?: () => void;
};

export function AutosaveIndicator({ status, onRetry }: AutosaveIndicatorProps) {
  const message = getAutosaveMessage(status);
  if (!message) return null;

  return (
    <div
      className={cn(
        "flex items-center gap-2 text-xs",
        status === "saved" && "text-green-600 dark:text-green-400",
        status === "error" && "text-destructive",
        status === "offline" && "text-amber-600 dark:text-amber-400",
        status === "saving" && "text-muted-foreground",
      )}
      aria-live="polite"
    >
      {status === "saving" && <Loader2 className="h-3 w-3 animate-spin" />}
      {status === "saved" && <Check className="h-3 w-3" />}
      {status === "error" && <AlertCircle className="h-3 w-3" />}
      {status === "offline" && <CloudOff className="h-3 w-3" />}
      <span>{message}</span>
      {status === "error" && onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="underline underline-offset-2"
        >
          Retry
        </button>
      )}
    </div>
  );
}
