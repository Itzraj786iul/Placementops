"use client";

import * as React from "react";
import {
  type FieldValues,
  type UseFormReturn,
  useWatch,
} from "react-hook-form";

import { useAutosave } from "@/features/student-onboarding/hooks/use-autosave";
import { useInvalidateStudentQueries } from "@/features/student-onboarding/hooks/use-student-data";

/**
 * Debounced autosave for onboarding steps.
 * Avoids invalidate+reset loops that freeze inputs while typing.
 */
export function useStepAutosave<T extends FieldValues>(
  form: UseFormReturn<T>,
  profileId: string,
  saveFn: (data: T) => Promise<void>,
  enabled: boolean,
) {
  const { invalidateProfile } = useInvalidateStudentQueries();
  const saveFnRef = React.useRef(saveFn);
  saveFnRef.current = saveFn;

  const { status, save, retry } = useAutosave<T>(async (data) => {
    await saveFnRef.current(data);
    // Clear dirty without clobbering in-progress keystrokes from a refetch.
    form.reset(data);
    // Refresh completion % only — do not refetch the active step form data.
    await invalidateProfile();
  });

  const values = useWatch({ control: form.control });
  const isDirty = form.formState.isDirty;
  const isFirstRender = React.useRef(true);
  const trigger = form.trigger;

  React.useEffect(() => {
    if (!enabled) return;
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (!isDirty) return;

    void trigger().then((valid) => {
      if (valid) save(values as T);
    });
  }, [values, enabled, isDirty, save, trigger]);

  const retrySave = React.useCallback(() => {
    void trigger().then((valid) => {
      if (valid) retry(values as T);
    });
  }, [trigger, retry, values]);

  return { status, retrySave };
}
