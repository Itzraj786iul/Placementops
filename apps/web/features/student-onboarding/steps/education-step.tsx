"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import * as React from "react";
import { useForm } from "react-hook-form";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import {
  EDUCATION_TYPE_LABELS,
  NITRR_INSTITUTION_NAME,
  ONBOARDING_EDUCATION_TYPES,
} from "@/features/student-onboarding/constants";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import {
  useInvalidateStudentQueries,
  useStudentOnboardingData,
} from "@/features/student-onboarding/hooks/use-student-data";
import {
  createEducation,
  deleteEducation,
  updateEducation,
} from "@/features/student-onboarding/api/student-client";
import {
  educationRecordSchema,
  type EducationRecordValues,
} from "@/features/student-onboarding/schemas/onboarding-schemas";
import type {
  EducationRecord,
  EducationType,
} from "@/features/student-onboarding/types";

function requiresBoard(type: EducationType): boolean {
  return type === "SECONDARY" || type === "HIGHER_SECONDARY";
}

function defaultInstitution(type: EducationType): string {
  return type === "UNDERGRADUATE" ? NITRR_INSTITUTION_NAME : "";
}

export function EducationStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { education } = useStudentOnboardingData(profileId);
  const { invalidateSections } = useInvalidateStudentQueries();
  const [editingType, setEditingType] = React.useState<EducationType | null>(
    null,
  );

  if (education.isLoading) return <StepSkeleton />;

  return (
    <SectionCard
      title="Education History"
      description="Add your 10th, 12th, and undergraduate details."
      focusId="education-section"
      status={(education.data?.length ?? 0) > 0 ? "complete" : "not_started"}
    >
      <div className="grid gap-4">
        {ONBOARDING_EDUCATION_TYPES.map((type) => {
          const record = education.data?.find((r) => r.education_type === type);
          return (
            <EducationTypeCard
              key={type}
              type={type}
              record={record}
              isReadOnly={isReadOnly}
              isEditing={editingType === type}
              onEdit={() => setEditingType(type)}
              onCancel={() => setEditingType(null)}
              onSaved={async () => {
                setEditingType(null);
                invalidateSections(profileId, ["education"]);
              }}
            />
          );
        })}
      </div>
    </SectionCard>
  );
}

function EducationTypeCard({
  type,
  record,
  isReadOnly,
  isEditing,
  onEdit,
  onCancel,
  onSaved,
}: {
  type: EducationType;
  record?: EducationRecord;
  isReadOnly: boolean;
  isEditing: boolean;
  onEdit: () => void;
  onCancel: () => void;
  onSaved: () => Promise<void>;
}) {
  const { profileId } = useOnboarding();
  const showBoard = requiresBoard(type);
  const form = useForm<EducationRecordValues>({
    resolver: zodResolver(educationRecordSchema),
    defaultValues: {
      education_type: type,
      institution: defaultInstitution(type),
      board: "",
      passing_year: new Date().getFullYear(),
      percentage_or_cgpa: "",
    },
  });

  React.useEffect(() => {
    if (record) {
      form.reset({
        education_type: record.education_type,
        institution: record.institution,
        board: record.board,
        passing_year: record.passing_year,
        percentage_or_cgpa: record.percentage_or_cgpa,
      });
      return;
    }
    form.reset({
      education_type: type,
      institution: defaultInstitution(type),
      board: "",
      passing_year: new Date().getFullYear(),
      percentage_or_cgpa: "",
    });
  }, [record, form, type]);

  const onSubmit = form.handleSubmit(async (data) => {
    const payload = {
      ...data,
      // Board is school-exam only; API still requires a non-empty string.
      board: showBoard ? data.board!.trim() : "N/A",
    };
    if (record) {
      await updateEducation(profileId, record.id, payload);
    } else {
      await createEducation(profileId, payload);
    }
    await onSaved();
  });

  const handleDelete = async () => {
    if (!record) return;
    await deleteEducation(profileId, record.id);
    await onSaved();
  };

  return (
    <div className="rounded-lg border p-4">
      <div className="mb-3 flex items-center justify-between">
        <h4 className="font-medium">{EDUCATION_TYPE_LABELS[type]}</h4>
        {!isReadOnly && !isEditing && (
          <Button type="button" size="sm" variant="outline" onClick={onEdit}>
            {record ? "Edit" : "Add"}
          </Button>
        )}
      </div>
      {record && !isEditing ? (
        <div className="text-muted-foreground space-y-1 text-sm">
          <p>{record.institution}</p>
          <p>
            {showBoard && record.board && record.board !== "N/A"
              ? `${record.board} · `
              : ""}
            {record.passing_year} · {record.percentage_or_cgpa}
          </p>
        </div>
      ) : !isEditing ? (
        <p className="text-muted-foreground text-sm">No record added yet.</p>
      ) : null}
      {isEditing && (
        <form onSubmit={onSubmit} className="mt-4 grid gap-3 sm:grid-cols-2">
          <input type="hidden" {...form.register("education_type")} />
          <FormField
            label={type === "UNDERGRADUATE" ? "Institute" : "Institution"}
            required
            error={form.formState.errors.institution?.message}
          >
            <Input {...form.register("institution")} />
          </FormField>
          {showBoard ? (
            <FormField
              label="Board"
              required
              error={form.formState.errors.board?.message}
            >
              <Input
                placeholder="e.g. CBSE, State Board"
                {...form.register("board")}
              />
            </FormField>
          ) : null}
          <FormField
            label="Passing Year"
            required
            error={form.formState.errors.passing_year?.message}
          >
            <Input type="number" {...form.register("passing_year")} />
          </FormField>
          <FormField
            label={type === "UNDERGRADUATE" ? "CGPA" : "Percentage / CGPA"}
            required
            error={form.formState.errors.percentage_or_cgpa?.message}
          >
            <Input {...form.register("percentage_or_cgpa")} />
          </FormField>
          <div className="flex gap-2 sm:col-span-2">
            <Button type="submit" size="sm">
              Save
            </Button>
            <Button
              type="button"
              size="sm"
              variant="outline"
              onClick={onCancel}
            >
              Cancel
            </Button>
            {record && (
              <Button
                type="button"
                size="sm"
                variant="ghost"
                className="text-destructive"
                onClick={handleDelete}
              >
                Delete
              </Button>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
