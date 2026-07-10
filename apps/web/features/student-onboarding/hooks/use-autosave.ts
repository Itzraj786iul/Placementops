"use client";

import * as React from "react";

import { ApiError, isOfflineError } from "@/lib/api-client";

export type AutosaveStatus = "idle" | "saving" | "saved" | "error" | "offline";

export function useAutosave<T>(
  saveFn: (data: T) => Promise<void>,
  debounceMs = 800,
) {
  const [status, setStatus] = React.useState<AutosaveStatus>("idle");
  const timeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const savedTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );

  const clearTimers = React.useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (savedTimeoutRef.current) clearTimeout(savedTimeoutRef.current);
  }, []);

  React.useEffect(() => clearTimers, [clearTimers]);

  const save = React.useCallback(
    (data: T) => {
      clearTimers();
      timeoutRef.current = setTimeout(async () => {
        setStatus("saving");
        try {
          await saveFn(data);
          setStatus("saved");
          savedTimeoutRef.current = setTimeout(() => setStatus("idle"), 2000);
        } catch (error) {
          if (isOfflineError(error)) {
            setStatus("offline");
            return;
          }
          setStatus("error");
        }
      }, debounceMs);
    },
    [clearTimers, debounceMs, saveFn],
  );

  const retry = React.useCallback(
    (data: T) => {
      clearTimers();
      void (async () => {
        setStatus("saving");
        try {
          await saveFn(data);
          setStatus("saved");
          savedTimeoutRef.current = setTimeout(() => setStatus("idle"), 2000);
        } catch (error) {
          if (isOfflineError(error)) {
            setStatus("offline");
            return;
          }
          setStatus("error");
        }
      })();
    },
    [clearTimers, saveFn],
  );

  return {
    status,
    save,
    retry,
    errorMessage: status === "error" ? "Save failed" : null,
  };
}

export function getAutosaveMessage(status: AutosaveStatus): string | null {
  switch (status) {
    case "saving":
      return "Saving...";
    case "saved":
      return "Saved";
    case "error":
      return "Save failed";
    case "offline":
      return "Offline — changes queued";
    default:
      return null;
  }
}

export function isApiError(error: unknown): error is ApiError {
  return error instanceof ApiError;
}
