import { z } from "zod";

export const companyCreateSchema = z.object({
  name: z.string().min(1, "Company name is required").max(255),
  industry: z.string().max(150).optional().or(z.literal("")),
  website: z.string().url("Enter a valid URL").optional().or(z.literal("")),
  linkedin: z.string().url("Enter a valid URL").optional().or(z.literal("")),
  headquarters: z.string().max(255).optional().or(z.literal("")),
  company_type: z.string().max(100).optional().or(z.literal("")),
  assignSelfAsHandler: z.boolean(),
  handler_user_id: z.string().uuid().optional().or(z.literal("")),
  branch: z.string().max(100).optional().or(z.literal("")),
  ownership_type: z.enum(["LEGACY", "NEW", "TRANSFERRED"]),
});

export const companyUpdateSchema = z.object({
  name: z.string().min(1).max(255).optional(),
  industry: z.string().max(150).optional().or(z.literal("")),
  website: z.string().url().optional().or(z.literal("")),
  linkedin: z.string().url().optional().or(z.literal("")),
  headquarters: z.string().max(255).optional().or(z.literal("")),
  company_type: z.string().max(100).optional().or(z.literal("")),
  status: z.enum(["ACTIVE", "INACTIVE"]).optional(),
});

export const contactCreateSchema = z.object({
  name: z.string().min(1, "Name is required").max(150),
  designation: z.string().max(150).optional().or(z.literal("")),
  email: z.string().email("Enter a valid email").optional().or(z.literal("")),
  phone: z.string().max(20).optional().or(z.literal("")),
  linkedin: z.string().url("Enter a valid URL").optional().or(z.literal("")),
  is_primary: z.boolean(),
  notes: z.string().optional().or(z.literal("")),
});

export const communicationCreateSchema = z.object({
  type: z.enum(["EMAIL", "CALL", "MEETING", "WHATSAPP", "OTHER"]),
  subject: z.string().max(255).optional().or(z.literal("")),
  description: z.string().min(1, "Description is required"),
  communication_date: z.string().min(1, "Date is required"),
});

export const documentCreateSchema = z.object({
  document_type: z.enum([
    "JD",
    "ELIGIBILITY",
    "PPT",
    "OFFER_TEMPLATE",
    "BOND",
    "OTHER",
  ]),
  file_url: z.string().url("Enter a valid file URL"),
});

export const pipelineUpdateSchema = z.object({
  current_stage: z.enum([
    "NOT_CONTACTED",
    "INVITATION_SENT",
    "FOLLOW_UP_PENDING",
    "HR_REPLIED",
    "MEETING_SCHEDULED",
    "INTERESTED",
    "ON_HOLD",
    "REJECTED",
    "DRIVE_PLANNED",
  ]),
});

export const handlerAssignSchema = z.object({
  handler_user_id: z.string().uuid("Enter a valid handler user ID"),
  branch: z.string().max(100).optional().or(z.literal("")),
  ownership_type: z.enum(["LEGACY", "NEW", "TRANSFERRED"]),
});

export type CompanyCreateValues = z.infer<typeof companyCreateSchema>;
export type CompanyUpdateValues = z.infer<typeof companyUpdateSchema>;
export type ContactCreateValues = z.infer<typeof contactCreateSchema>;
export type CommunicationCreateValues = z.infer<
  typeof communicationCreateSchema
>;
export type DocumentCreateValues = z.infer<typeof documentCreateSchema>;
export type PipelineUpdateValues = z.infer<typeof pipelineUpdateSchema>;
export type HandlerAssignValues = z.infer<typeof handlerAssignSchema>;
