"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import * as React from "react";
import { useForm } from "react-hook-form";

import { Input } from "@/components/ui/input";
import { AutosaveIndicator } from "@/features/student-onboarding/components/autosave-indicator";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import { useStepAutosave } from "@/features/student-onboarding/hooks/use-step-autosave";
import { useStudentOnboardingData } from "@/features/student-onboarding/hooks/use-student-data";
import { saveAcademicInfo } from "@/features/student-onboarding/api/student-client";
import {
  academicInfoSchema,
  type AcademicInfoValues,
} from "@/features/student-onboarding/schemas/onboarding-schemas";
import { ApiError } from "@/lib/api-client";

const DEFAULT_VALUES: AcademicInfoValues = {
  current_cgpa: 0,
  semester: 1,
  active_backlogs: 0,
  total_history_backlogs: 0,
};

export function AcademicStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { academic } = useStudentOnboardingData(profileId);
  const form = useForm<AcademicInfoValues>({
    resolver: zodResolver(academicInfoSchema),
    defaultValues: DEFAULT_VALUES,
    mode: "onBlur",
  });

  const { register, formState, reset } = form;
  const hydrated = React.useRef(false);

  React.useEffect(() => {
    if (!academic.data || hydrated.current || form.formState.isDirty) return;
    reset({
      current_cgpa: Number(academic.data.current_cgpa),
      semester: academic.data.semester,
      active_backlogs: academic.data.active_backlogs,
      total_history_backlogs: academic.data.total_history_backlogs,
    });
    hydrated.current = true;
  }, [academic.data, reset, form.formState.isDirty]);

  const saveAcademic = React.useCallback(
    async (data: AcademicInfoValues) => {
      await saveAcademicInfo(profileId, {
        current_cgpa: String(data.current_cgpa),
        semester: data.semester,
        active_backlogs: data.active_backlogs,
        total_history_backlogs: data.total_history_backlogs,
      });
    },
    [profileId],
  );

  const { status, retrySave } = useStepAutosave(
    form,
    profileId,
    saveAcademic,
    !isReadOnly,
    ["academic"],
  );

  if (academic.isLoading) return <StepSkeleton />;

  const notFound =
    academic.isError &&
    academic.error instanceof ApiError &&
    academic.error.statusCode === 404;

  if (academic.isError && !notFound) {
    return (
      <p className="text-destructive text-sm">
        Failed to load academic information.
      </p>
    );
  }

  return (
    <SectionCard
      title="Academic Information"
      description="Your current academic standing at the institute."
      focusId="academic-section"
      status={academic.data ? "complete" : "not_started"}
    >
      <div className="mb-6 flex justify-end">
        <AutosaveIndicator status={status} onRetry={retrySave} />
      </div>
      <form className="grid gap-4 sm:grid-cols-2">
        <FormField
          label="Current CGPA"
          htmlFor="current_cgpa"
          required
          error={formState.errors.current_cgpa?.message}
        >
          <Input
            id="current_cgpa"
            type="number"
            step="0.01"
            min={0}
            max={10}
            disabled={isReadOnly}
            {...register("current_cgpa")}
          />
        </FormField>
        <FormField
          label="Semester"
          htmlFor="semester"
          required
          error={formState.errors.semester?.message}
        >
          <Input
            id="semester"
            type="number"
            min={1}
            max={12}
            disabled={isReadOnly}
            {...register("semester")}
          />
        </FormField>
        <FormField
          label="Active Backlogs"
          htmlFor="active_backlogs"
          required
          error={formState.errors.active_backlogs?.message}
        >
          <Input
            id="active_backlogs"
            type="number"
            min={0}
            disabled={isReadOnly}
            {...register("active_backlogs")}
          />
        </FormField>
        <FormField
          label="History of Backlogs"
          htmlFor="total_history_backlogs"
          required
          error={formState.errors.total_history_backlogs?.message}
        >
          <Input
            id="total_history_backlogs"
            type="number"
            min={0}
            disabled={isReadOnly}
            {...register("total_history_backlogs")}
          />
        </FormField>
      </form>
    </SectionCard>
  );
}
