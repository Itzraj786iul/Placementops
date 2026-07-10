"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { SlideOver } from "@/features/company-crm/components/slide-over";
import {
  COMMUNICATION_TYPES,
  DOCUMENT_LABELS,
  DOCUMENT_TYPES,
  PIPELINE_LABELS,
  PIPELINE_STAGES,
} from "@/features/company-crm/constants";
import { useCompanyMutations } from "@/features/company-crm/hooks/use-companies";
import { useCreateContact } from "@/features/company-crm/hooks/use-company-contacts";
import { useCreateCommunication } from "@/features/company-crm/hooks/use-company-timeline";
import { createDocument } from "@/features/company-crm/api/company-client";
import {
  communicationCreateSchema,
  companyUpdateSchema,
  contactCreateSchema,
  documentCreateSchema,
  handlerAssignSchema,
  pipelineUpdateSchema,
  type CommunicationCreateValues,
  type CompanyUpdateValues,
  type ContactCreateValues,
  type DocumentCreateValues,
  type HandlerAssignValues,
  type PipelineUpdateValues,
} from "@/features/company-crm/schemas/company-schemas";
import { updatePipeline } from "@/features/company-crm/api/company-client";
import type { Company, CompanyDocument } from "@/features/company-crm/types";
import { useAuth } from "@/providers/auth-provider";
import { useQueryClient } from "@tanstack/react-query";
import { companyQueryKeys } from "@/features/company-crm/hooks/use-companies";

type ActionSheetsProps = {
  company: Company | null;
  companyId: string | null;
  activeSheet: string | null;
  onClose: () => void;
  onDocumentUploaded: (doc: CompanyDocument) => void;
};

export function ActionSheets({
  company,
  companyId,
  activeSheet,
  onClose,
  onDocumentUploaded,
}: ActionSheetsProps) {
  const { user } = useAuth();
  const { update } = useCompanyMutations();
  const queryClient = useQueryClient();
  const createContact = useCreateContact(companyId ?? "");
  const createCommunication = useCreateCommunication(companyId ?? "");

  const editForm = useForm<CompanyUpdateValues>({
    resolver: zodResolver(companyUpdateSchema),
    values: company
      ? {
          name: company.name,
          industry: company.industry ?? "",
          website: company.website ?? "",
          linkedin: company.linkedin ?? "",
          headquarters: company.headquarters ?? "",
          company_type: company.company_type ?? "",
          status: company.status,
        }
      : undefined,
  });

  const pipelineForm = useForm<PipelineUpdateValues>({
    resolver: zodResolver(pipelineUpdateSchema),
    values: {
      current_stage: company?.pipeline?.current_stage ?? "NOT_CONTACTED",
    },
  });

  const handlerForm = useForm<HandlerAssignValues>({
    resolver: zodResolver(handlerAssignSchema),
    defaultValues: {
      handler_user_id: user?.id ?? "",
      branch: "",
      ownership_type: "NEW",
    },
  });

  const contactForm = useForm<ContactCreateValues>({
    resolver: zodResolver(contactCreateSchema),
    defaultValues: {
      name: "",
      designation: "",
      email: "",
      phone: "",
      linkedin: "",
      is_primary: false,
      notes: "",
    },
  });

  const commForm = useForm<CommunicationCreateValues>({
    resolver: zodResolver(communicationCreateSchema),
    defaultValues: {
      type: "EMAIL",
      subject: "",
      description: "",
      communication_date: new Date().toISOString().slice(0, 16),
    },
  });

  const docForm = useForm<DocumentCreateValues>({
    resolver: zodResolver(documentCreateSchema),
    defaultValues: { document_type: "JD", file_url: "" },
  });

  if (!companyId) return null;

  return (
    <>
      <SlideOver
        open={activeSheet === "edit"}
        onClose={onClose}
        title="Edit Company"
      >
        <form
          onSubmit={editForm.handleSubmit(async (data) => {
            try {
              await update.mutateAsync({
                id: companyId,
                payload: {
                  name: data.name,
                  industry: data.industry || null,
                  website: data.website || null,
                  linkedin: data.linkedin || null,
                  headquarters: data.headquarters || null,
                  company_type: data.company_type || null,
                  status: data.status,
                },
              });
              toast.success("Company updated");
              onClose();
            } catch {
              toast.error("Update failed");
            }
          })}
          className="space-y-3"
        >
          <Input {...editForm.register("name")} placeholder="Name" />
          <Input {...editForm.register("industry")} placeholder="Industry" />
          <Input {...editForm.register("website")} placeholder="Website" />
          <Input {...editForm.register("linkedin")} placeholder="LinkedIn" />
          <Input
            {...editForm.register("headquarters")}
            placeholder="Headquarters"
          />
          <Input
            {...editForm.register("company_type")}
            placeholder="Company type"
          />
          <Select {...editForm.register("status")}>
            <option value="ACTIVE">Active</option>
            <option value="INACTIVE">Inactive</option>
          </Select>
          <Button type="submit" className="w-full">
            Save Changes
          </Button>
        </form>
      </SlideOver>

      <SlideOver
        open={activeSheet === "pipeline"}
        onClose={onClose}
        title="Update Pipeline"
      >
        <form
          onSubmit={pipelineForm.handleSubmit(async (data) => {
            try {
              await updatePipeline(companyId, data);
              await queryClient.invalidateQueries({
                queryKey: companyQueryKeys.detail(companyId),
              });
              await queryClient.invalidateQueries({
                queryKey: companyQueryKeys.all,
              });
              toast.success("Pipeline updated");
              onClose();
            } catch {
              toast.error("Pipeline update failed");
            }
          })}
          className="space-y-3"
        >
          <Select {...pipelineForm.register("current_stage")}>
            {PIPELINE_STAGES.map((s) => (
              <option key={s} value={s}>
                {PIPELINE_LABELS[s]}
              </option>
            ))}
          </Select>
          <Button type="submit" className="w-full">
            Update Stage
          </Button>
        </form>
      </SlideOver>

      <SlideOver
        open={activeSheet === "handler"}
        onClose={onClose}
        title="Assign Handler"
      >
        <form
          onSubmit={handlerForm.handleSubmit(async (data) => {
            try {
              await update.mutateAsync({
                id: companyId,
                payload: {
                  handler: {
                    handler_user_id: data.handler_user_id,
                    branch: data.branch || null,
                    ownership_type: data.ownership_type,
                  },
                },
              });
              toast.success("Handler assigned");
              onClose();
            } catch {
              toast.error("Handler assignment failed");
            }
          })}
          className="space-y-3"
        >
          <Input
            {...handlerForm.register("handler_user_id")}
            placeholder="Handler user ID"
          />
          <Input {...handlerForm.register("branch")} placeholder="Branch" />
          <Select {...handlerForm.register("ownership_type")}>
            <option value="NEW">New</option>
            <option value="LEGACY">Legacy</option>
            <option value="TRANSFERRED">Transferred</option>
          </Select>
          <Button type="submit" className="w-full">
            Assign
          </Button>
        </form>
      </SlideOver>

      <SlideOver
        open={activeSheet === "contact"}
        onClose={onClose}
        title="Add Contact"
      >
        <form
          onSubmit={contactForm.handleSubmit(async (data) => {
            try {
              await createContact.mutateAsync({
                name: data.name,
                designation: data.designation || null,
                email: data.email || null,
                phone: data.phone || null,
                linkedin: data.linkedin || null,
                is_primary: data.is_primary,
                notes: data.notes || null,
              });
              toast.success("Contact added");
              contactForm.reset();
              onClose();
            } catch {
              toast.error("Failed to add contact");
            }
          })}
          className="space-y-3"
        >
          <Input {...contactForm.register("name")} placeholder="Name" />
          <Input
            {...contactForm.register("designation")}
            placeholder="Designation"
          />
          <Input {...contactForm.register("email")} placeholder="Email" />
          <Input {...contactForm.register("phone")} placeholder="Phone" />
          <Input
            {...contactForm.register("linkedin")}
            placeholder="LinkedIn URL"
          />
          <Textarea {...contactForm.register("notes")} placeholder="Notes" />
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" {...contactForm.register("is_primary")} />
            Primary contact
          </label>
          <Button type="submit" className="w-full">
            Add Contact
          </Button>
        </form>
      </SlideOver>

      <SlideOver
        open={activeSheet === "communication"}
        onClose={onClose}
        title="Add Communication"
      >
        <form
          onSubmit={commForm.handleSubmit(async (data) => {
            try {
              await createCommunication.mutateAsync({
                type: data.type,
                subject: data.subject || null,
                description: data.description,
                communication_date: new Date(
                  data.communication_date,
                ).toISOString(),
              });
              toast.success("Communication logged");
              commForm.reset();
              onClose();
            } catch {
              toast.error("Failed to log communication");
            }
          })}
          className="space-y-3"
        >
          <Select {...commForm.register("type")}>
            {COMMUNICATION_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </Select>
          <Input {...commForm.register("subject")} placeholder="Subject" />
          <Textarea
            {...commForm.register("description")}
            placeholder="Description"
          />
          <Input
            type="datetime-local"
            {...commForm.register("communication_date")}
          />
          <Button type="submit" className="w-full">
            Log Communication
          </Button>
        </form>
      </SlideOver>

      <SlideOver
        open={activeSheet === "document"}
        onClose={onClose}
        title="Upload Document"
      >
        <form
          onSubmit={docForm.handleSubmit(async (data) => {
            try {
              const doc = await createDocument(companyId, data);
              onDocumentUploaded(doc);
              toast.success("Document uploaded");
              docForm.reset();
              onClose();
            } catch {
              toast.error("Upload failed");
            }
          })}
          className="space-y-3"
        >
          <Select {...docForm.register("document_type")}>
            {DOCUMENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {DOCUMENT_LABELS[t]}
              </option>
            ))}
          </Select>
          <Input {...docForm.register("file_url")} placeholder="File URL" />
          <Button type="submit" className="w-full">
            Upload
          </Button>
        </form>
      </SlideOver>
    </>
  );
}
