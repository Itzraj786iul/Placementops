"use client";

import * as React from "react";
import {
  type FieldValues,
  type UseFormReturn,
  useWatch,
} from "react-hook-form";

import { useAutosave } from "@/features/student-onboarding/hooks/use-autosave";
import {
  type StudentSectionKey,
  useInvalidateStudentQueries,
} from "@/features/student-onboarding/hooks/use-student-data";

/** Single debounce window — useAutosave runs immediately after this. */
const VALIDATE_DEBOUNCE_MS = 300;

/**
 * Debounced autosave for onboarding steps.
 * Optimistic local form state; serializes API writes; does not block UI on refetch.
 */
export function useStepAutosave<T extends FieldValues>(
  form: UseFormReturn<T>,
  profileId: string,
  saveFn: (data: T) => Promise<void>,
  enabled: boolean,
  sections: StudentSectionKey[] = [],
) {
  const { invalidateSections } = useInvalidateStudentQueries();
  const saveFnRef = React.useRef(saveFn);
  saveFnRef.current = saveFn;
  const formRef = React.useRef(form);
  formRef.current = form;
  const invalidateRef = React.useRef(invalidateSections);
  invalidateRef.current = invalidateSections;
  const profileIdRef = React.useRef(profileId);
  profileIdRef.current = profileId;
  const sectionsRef = React.useRef(sections);
  sectionsRef.current = sections;

  const persist = React.useCallback(async (data: T) => {
    await saveFnRef.current(data);
    // Keep in-progress edits; mark current values as the saved baseline.
    formRef.current.reset(data, { keepValues: true });
    // Refresh completion + this section only — do not delay "Saved".
    invalidateRef.current(profileIdRef.current, sectionsRef.current);
  }, []);

  // Debounce lives in useStepAutosave; pass 0 here to avoid a second delay.
  const { status, save, retry } = useAutosave<T>(persist, 0);
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
        saveRef.current(formRef.current.getValues());
      });
    }, VALIDATE_DEBOUNCE_MS);

    return () => clearTimeout(handle);
  }, [values, enabled, isDirty]);

  const retrySave = React.useCallback(() => {
    void formRef.current.trigger().then((valid) => {
      if (valid) retryRef.current(formRef.current.getValues());
    });
  }, []);

  return { status, retrySave };
}
