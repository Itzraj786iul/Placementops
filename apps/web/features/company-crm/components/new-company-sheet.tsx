"use client";

import * as React from "react";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { SlideOver } from "@/features/company-crm/components/slide-over";
import { useCompanyMutations } from "@/features/company-crm/hooks/use-companies";
import {
  companyCreateSchema,
  type CompanyCreateValues,
} from "@/features/company-crm/schemas/company-schemas";
import { useAuth } from "@/providers/auth-provider";

type NewCompanySheetProps = {
  open: boolean;
  onClose: () => void;
  onCreated: (companyId: string) => void;
};

export function NewCompanySheet({
  open,
  onClose,
  onCreated,
}: NewCompanySheetProps) {
  const { user } = useAuth();
  const { create } = useCompanyMutations();

  const form = useForm<CompanyCreateValues>({
    resolver: zodResolver(companyCreateSchema),
    defaultValues: {
      name: "",
      industry: "",
      website: "",
      linkedin: "",
      headquarters: "",
      company_type: "",
      assignSelfAsHandler: true,
      handler_user_id: "",
      branch: "",
      ownership_type: "NEW",
    },
  });

  const onSubmit = form.handleSubmit(async (data) => {
    try {
      const handlerId = data.assignSelfAsHandler
        ? user?.id
        : data.handler_user_id?.trim() || undefined;

      const result = await create.mutateAsync({
        name: data.name,
        industry: data.industry || null,
        website: data.website || null,
        linkedin: data.linkedin || null,
        headquarters: data.headquarters || null,
        company_type: data.company_type || null,
        handler: handlerId
          ? {
              handler_user_id: handlerId,
              branch: data.branch || null,
              ownership_type: data.ownership_type,
            }
          : undefined,
      });
      toast.success("Company created");
      form.reset();
      onClose();
      onCreated(result.id);
    } catch {
      toast.error("Failed to create company");
    }
  });

  return (
    <SlideOver
      open={open}
      onClose={onClose}
      title="New Company"
      description="Add a company to your CRM pipeline."
    >
      <form onSubmit={onSubmit} className="space-y-4">
        <Field label="Company Name" error={form.formState.errors.name?.message}>
          <Input {...form.register("name")} />
        </Field>
        <Field label="Industry" error={form.formState.errors.industry?.message}>
          <Input {...form.register("industry")} />
        </Field>
        <Field label="Website" error={form.formState.errors.website?.message}>
          <Input {...form.register("website")} placeholder="https://" />
        </Field>
        <Field label="LinkedIn" error={form.formState.errors.linkedin?.message}>
          <Input {...form.register("linkedin")} placeholder="https://" />
        </Field>
        <Field label="Headquarters">
          <Input {...form.register("headquarters")} />
        </Field>
        <Field label="Company Type">
          <Input
            {...form.register("company_type")}
            placeholder="e.g. Product, MNC"
          />
        </Field>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" {...form.register("assignSelfAsHandler")} />
          Assign me as handler
        </label>
        {!form.watch("assignSelfAsHandler") && (
          <Field
            label="Handler User ID"
            error={form.formState.errors.handler_user_id?.message}
          >
            <Input {...form.register("handler_user_id")} placeholder="UUID" />
          </Field>
        )}
        <Field label="Branch">
          <Input {...form.register("branch")} />
        </Field>
        <Field label="Ownership Type">
          <Select {...form.register("ownership_type")}>
            <option value="NEW">New</option>
            <option value="LEGACY">Legacy</option>
            <option value="TRANSFERRED">Transferred</option>
          </Select>
        </Field>
        <Button type="submit" className="w-full" disabled={create.isPending}>
          {create.isPending ? "Creating..." : "Create Company"}
        </Button>
      </form>
    </SlideOver>
  );
}

function Field({
  label,
  error,
  children,
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) {
  return (
    <div className="space-y-1.5">
      <label className="text-sm font-medium">{label}</label>
      {children}
      {error && <p className="text-destructive text-xs">{error}</p>}
    </div>
  );
}
