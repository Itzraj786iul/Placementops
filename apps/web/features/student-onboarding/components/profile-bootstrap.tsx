"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import { createProfile } from "@/features/student-onboarding/api/student-client";
import {
  useDepartments,
  useInvalidateStudentQueries,
} from "@/features/student-onboarding/hooks/use-student-data";
import {
  profileBootstrapSchema,
  type ProfileBootstrapValues,
} from "@/features/student-onboarding/schemas/onboarding-schemas";
import { ApiError } from "@/lib/api-client";

export function ProfileBootstrap({ onCreated }: { onCreated: () => void }) {
  const { data: departments, isLoading } = useDepartments();
  const { invalidateProfile } = useInvalidateStudentQueries();

  const form = useForm<ProfileBootstrapValues>({
    resolver: zodResolver(profileBootstrapSchema),
    defaultValues: {
      department_id: "",
      roll_number: "",
      registration_number: "",
      graduation_year: new Date().getFullYear() + 1,
    },
  });

  const mutation = useMutation({
    mutationFn: createProfile,
    onSuccess: async () => {
      await invalidateProfile();
      onCreated();
    },
  });

  const onSubmit = form.handleSubmit((data) => {
    mutation.mutate(data);
  });

  if (isLoading) return <StepSkeleton />;

  return (
    <SectionCard
      title="Set Up Your Profile"
      description="Enter your institute details to begin onboarding."
    >
      <form onSubmit={onSubmit} className="grid max-w-lg gap-4">
        <FormField
          label="Department"
          error={form.formState.errors.department_id?.message}
        >
          <Select {...form.register("department_id")}>
            <option value="">Select department</option>
            {departments?.map((dept) => (
              <option key={dept.id} value={dept.id}>
                {dept.name} ({dept.code})
              </option>
            ))}
          </Select>
        </FormField>
        <FormField
          label="Roll Number"
          error={form.formState.errors.roll_number?.message}
        >
          <Input {...form.register("roll_number")} />
        </FormField>
        <FormField
          label="Registration Number"
          error={form.formState.errors.registration_number?.message}
        >
          <Input {...form.register("registration_number")} />
        </FormField>
        <FormField
          label="Graduation Year"
          error={form.formState.errors.graduation_year?.message}
        >
          <Input type="number" {...form.register("graduation_year")} />
        </FormField>
        {mutation.error && (
          <p className="text-destructive text-sm" role="alert">
            {mutation.error instanceof ApiError
              ? mutation.error.message
              : "Failed to create profile"}
          </p>
        )}
        <Button type="submit" disabled={mutation.isPending}>
          {mutation.isPending ? "Creating..." : "Start Onboarding"}
        </Button>
      </form>
    </SectionCard>
  );
}
