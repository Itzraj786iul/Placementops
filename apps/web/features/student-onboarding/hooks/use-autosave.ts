"use client";

import * as React from "react";

import { ApiError, isOfflineError } from "@/lib/api-client";

export type AutosaveStatus = "idle" | "saving" | "saved" | "error" | "offline";

/**
 * Latest-wins autosave with optional debounce.
 * Never runs overlapping saves; coalesces rapid edits into one request.
 */
export function useAutosave<T>(
  saveFn: (data: T) => Promise<void>,
  debounceMs = 300,
) {
  const [status, setStatus] = React.useState<AutosaveStatus>("idle");
  const timeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(null);
  const savedTimeoutRef = React.useRef<ReturnType<typeof setTimeout> | null>(
    null,
  );
  const saveFnRef = React.useRef(saveFn);
  saveFnRef.current = saveFn;

  const inFlightRef = React.useRef(false);
  const queuedRef = React.useRef<T | null>(null);

  const clearTimers = React.useCallback(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    if (savedTimeoutRef.current) clearTimeout(savedTimeoutRef.current);
    timeoutRef.current = null;
    savedTimeoutRef.current = null;
  }, []);

  React.useEffect(() => clearTimers, [clearTimers]);

  const flush = React.useCallback(async (data: T) => {
    if (inFlightRef.current) {
      queuedRef.current = data;
      return;
    }

    inFlightRef.current = true;
    queuedRef.current = null;
    setStatus("saving");

    try {
      let payload: T | null = data;
      while (payload !== null) {
        await saveFnRef.current(payload);
        payload = queuedRef.current;
        queuedRef.current = null;
      }
      setStatus("saved");
      savedTimeoutRef.current = setTimeout(() => setStatus("idle"), 1500);
    } catch (error) {
      queuedRef.current = null;
      if (isOfflineError(error)) {
        setStatus("offline");
      } else {
        setStatus("error");
      }
    } finally {
      inFlightRef.current = false;
    }
  }, []);

  const save = React.useCallback(
    (data: T) => {
      clearTimers();
      timeoutRef.current = setTimeout(() => {
        void flush(data);
      }, debounceMs);
    },
    [clearTimers, debounceMs, flush],
  );

  const retry = React.useCallback(
    (data: T) => {
      clearTimers();
      void flush(data);
    },
    [clearTimers, flush],
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
