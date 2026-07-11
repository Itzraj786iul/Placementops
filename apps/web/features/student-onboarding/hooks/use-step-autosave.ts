"use client";

import * as React from "react";
import {
  type FieldValues,
  type UseFormReturn,
  useWatch,
} from "react-hook-form";

import { useAutosave } from "@/features/student-onboarding/hooks/use-autosave";
import { useInvalidateStudentQueries } from "@/features/student-onboarding/hooks/use-student-data";

const VALIDATE_DEBOUNCE_MS = 400;

/**
 * Debounced autosave for onboarding steps.
 * Stabilized against render loops that freeze inputs while typing.
 */
export function useStepAutosave<T extends FieldValues>(
  form: UseFormReturn<T>,
  _profileId: string,
  saveFn: (data: T) => Promise<void>,
  enabled: boolean,
) {
  const { invalidateProfile } = useInvalidateStudentQueries();
  const saveFnRef = React.useRef(saveFn);
  saveFnRef.current = saveFn;
  const formRef = React.useRef(form);
  formRef.current = form;
  const invalidateRef = React.useRef(invalidateProfile);
  invalidateRef.current = invalidateProfile;

  const persist = React.useCallback(async (data: T) => {
    await saveFnRef.current(data);
    // Keep whatever the user typed during the request; update defaults to saved data.
    formRef.current.reset(data, { keepValues: true });
    await invalidateRef.current();
  }, []);

  const { status, save, retry } = useAutosave<T>(persist);
  const saveRef = React.useRef(save);
  saveRef.current = save;
  const retryRef = React.useRef(retry);
  retryRef.current = retry;

  const values = useWatch({ control: form.control });
  const isDirty = form.formState.isDirty;
  const isFirstRender = React.useRef(true);

  React.useEffect(() => {
    if (!enabled) return;
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (!isDirty) return;

    const handle = setTimeout(() => {
      void formRef.current.trigger().then((valid) => {
        if (!valid) return;
        // Always read latest values — effect closure can be stale after await.
        saveRef.current(formRef.current.getValues());
      });
    }, VALIDATE_DEBOUNCE_MS);

    return () => clearTimeout(handle);
    // Intentionally omit save/trigger — refs keep them current without re-firing.
  }, [values, enabled, isDirty]);

  const retrySave = React.useCallback(() => {
    void formRef.current.trigger().then((valid) => {
      if (valid) retryRef.current(formRef.current.getValues());
    });
  }, []);

  return { status, retrySave };
}
