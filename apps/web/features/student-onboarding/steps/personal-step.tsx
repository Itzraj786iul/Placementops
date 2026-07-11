"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import * as React from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { FileUpload } from "@/components/ui/file-upload";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { AutosaveIndicator } from "@/features/student-onboarding/components/autosave-indicator";
import { FormField } from "@/features/student-onboarding/components/form-field";
import { SectionCard } from "@/features/student-onboarding/components/section-card";
import { StepSkeleton } from "@/features/student-onboarding/components/step-skeleton";
import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";
import { useStepAutosave } from "@/features/student-onboarding/hooks/use-step-autosave";
import { useStudentOnboardingData } from "@/features/student-onboarding/hooks/use-student-data";
import {
  savePersonalInfo,
  uploadProfilePhoto,
} from "@/features/student-onboarding/api/student-client";
import {
  personalInfoSchema,
  type PersonalInfoValues,
} from "@/features/student-onboarding/schemas/onboarding-schemas";
import { nullifyEmpty } from "@/features/student-onboarding/utils/payload-helpers";
import { ApiError } from "@/lib/api-client";

const DEFAULT_VALUES: PersonalInfoValues = {
  first_name: "",
  last_name: "",
  gender: "MALE",
  date_of_birth: "",
  phone_number: "",
  alternate_phone: "",
  personal_email: "",
  address: "",
  city: "",
  state: "",
  country: "India",
  photo_url: "",
};

export function PersonalStep() {
  const { profileId, isReadOnly } = useOnboarding();
  const { personal } = useStudentOnboardingData(profileId);
  const form = useForm<PersonalInfoValues>({
    resolver: zodResolver(personalInfoSchema),
    defaultValues: DEFAULT_VALUES,
    mode: "onBlur",
  });

  const { register, formState, reset, setValue, watch } = form;
  const photoUrl = watch("photo_url");
  const hydratedKey = React.useRef<string | null>(null);

  React.useEffect(() => {
    if (!personal.data) return;
    // Hydrate once per loaded record — never reset while the user is editing.
    const key = personal.data.student_profile_id;
    if (hydratedKey.current === key) return;
    if (form.formState.isDirty) return;

    reset({
      first_name: personal.data.first_name,
      last_name: personal.data.last_name,
      gender: personal.data.gender,
      date_of_birth: personal.data.date_of_birth,
      phone_number: personal.data.phone_number,
      alternate_phone: personal.data.alternate_phone ?? "",
      personal_email: personal.data.personal_email ?? "",
      address: personal.data.address,
      city: personal.data.city,
      state: personal.data.state,
      country: personal.data.country,
      photo_url: personal.data.photo_url ?? "",
    });
    hydratedKey.current = key;
  }, [personal.data, reset, form.formState.isDirty]);

  const { status, retrySave } = useStepAutosave(
    form,
    profileId,
    async (data) => {
      await savePersonalInfo(profileId, {
        ...data,
        alternate_phone: nullifyEmpty(data.alternate_phone),
        personal_email: nullifyEmpty(data.personal_email),
        photo_url: nullifyEmpty(data.photo_url),
      });
    },
    !isReadOnly,
  );

  if (personal.isLoading) return <StepSkeleton />;

  const notFound =
    personal.isError &&
    personal.error instanceof ApiError &&
    personal.error.statusCode === 404;

  if (personal.isError && !notFound) {
    return (
      <p className="text-destructive text-sm">
        Failed to load personal information.
      </p>
    );
  }

  return (
    <SectionCard
      title="Personal Information"
      description="Your contact details and identity information."
    >
      <div className="mb-6 flex justify-end">
        <AutosaveIndicator status={status} onRetry={retrySave} />
      </div>
      <form className="grid gap-4 sm:grid-cols-2">
        <FormField
          label="Profile Photo"
          htmlFor="photo_upload"
          className="sm:col-span-2"
        >
          <div className="space-y-3">
            {photoUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={photoUrl}
                alt="Profile"
                className="h-24 w-24 rounded-full border object-cover"
              />
            ) : null}
            {!isReadOnly && (
              <FileUpload
                category="image"
                label="Upload a profile photo"
                hint="PNG or JPG · max 5 MB"
                onUpload={async (file, onProgress) => {
                  const result = await uploadProfilePhoto(
                    profileId,
                    file,
                    onProgress,
                  );
                  setValue("photo_url", result.photo_url, {
                    shouldDirty: true,
                    shouldValidate: true,
                  });
                  toast.success("Photo uploaded");
                }}
              />
            )}
          </div>
        </FormField>
        <FormField
          label="First Name"
          htmlFor="first_name"
          error={formState.errors.first_name?.message}
        >
          <Input
            id="first_name"
            autoComplete="given-name"
            disabled={isReadOnly}
            {...register("first_name")}
          />
        </FormField>
        <FormField
          label="Last Name"
          htmlFor="last_name"
          error={formState.errors.last_name?.message}
        >
          <Input
            id="last_name"
            autoComplete="family-name"
            disabled={isReadOnly}
            {...register("last_name")}
          />
        </FormField>
        <FormField
          label="Gender"
          htmlFor="gender"
          error={formState.errors.gender?.message}
        >
          <Select id="gender" disabled={isReadOnly} {...register("gender")}>
            <option value="MALE">Male</option>
            <option value="FEMALE">Female</option>
            <option value="OTHER">Other</option>
          </Select>
        </FormField>
        <FormField
          label="Date of Birth"
          htmlFor="date_of_birth"
          error={formState.errors.date_of_birth?.message}
        >
          <Input
            id="date_of_birth"
            type="date"
            disabled={isReadOnly}
            {...register("date_of_birth")}
          />
        </FormField>
        <FormField
          label="Phone"
          htmlFor="phone_number"
          error={formState.errors.phone_number?.message}
        >
          <Input
            id="phone_number"
            disabled={isReadOnly}
            {...register("phone_number")}
          />
        </FormField>
        <FormField label="Alternate Phone" htmlFor="alternate_phone">
          <Input
            id="alternate_phone"
            disabled={isReadOnly}
            {...register("alternate_phone")}
          />
        </FormField>
        <FormField
          label="Personal Email"
          htmlFor="personal_email"
          error={formState.errors.personal_email?.message}
        >
          <Input
            id="personal_email"
            type="email"
            disabled={isReadOnly}
            {...register("personal_email")}
          />
        </FormField>
        <FormField
          label="Address"
          htmlFor="address"
          error={formState.errors.address?.message}
          className="sm:col-span-2"
        >
          <Textarea
            id="address"
            disabled={isReadOnly}
            {...register("address")}
          />
        </FormField>
        <FormField
          label="City"
          htmlFor="city"
          error={formState.errors.city?.message}
        >
          <Input id="city" disabled={isReadOnly} {...register("city")} />
        </FormField>
        <FormField
          label="State"
          htmlFor="state"
          error={formState.errors.state?.message}
        >
          <Input id="state" disabled={isReadOnly} {...register("state")} />
        </FormField>
        <FormField
          label="Country"
          htmlFor="country"
          error={formState.errors.country?.message}
        >
          <Input id="country" disabled={isReadOnly} {...register("country")} />
        </FormField>
      </form>
    </SectionCard>
  );
}
