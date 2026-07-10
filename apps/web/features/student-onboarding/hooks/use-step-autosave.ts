"use client";

import * as React from "react";
import {
  type FieldValues,
  type UseFormReturn,
  useWatch,
} from "react-hook-form";

import { useAutosave } from "@/features/student-onboarding/hooks/use-autosave";
import { useInvalidateStudentQueries } from "@/features/student-onboarding/hooks/use-student-data";

export function useStepAutosave<T extends FieldValues>(
  form: UseFormReturn<T>,
  profileId: string,
  saveFn: (data: T) => Promise<void>,
  enabled: boolean,
) {
  const { invalidateAll } = useInvalidateStudentQueries();
  const { status, save, retry } = useAutosave<T>(async (data) => {
    await saveFn(data);
    await invalidateAll(profileId);
  });
  const values = useWatch({ control: form.control });
  const isFirstRender = React.useRef(true);

  React.useEffect(() => {
    if (!enabled) return;
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }
    if (!form.formState.isDirty) return;

    void form.trigger().then((valid) => {
      if (valid) save(values as T);
    });
  }, [values, enabled, form, save]);

  const retrySave = React.useCallback(() => {
    void form.trigger().then((valid) => {
      if (valid) retry(values as T);
    });
  }, [form, retry, values]);

  return { status, retrySave };
}
