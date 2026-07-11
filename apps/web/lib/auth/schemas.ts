import { z } from "zod";

export const roleSchema = z.object({
  id: z.string().uuid(),
  name: z.enum([
    "SUPER_ADMIN",
    "PLACEMENT_CELL",
    "PLACEMENT_CONVENER",
    "STUDENT",
  ]),
  description: z.string(),
});

export const userSchema = z.object({
  id: z.string().uuid(),
  college_email: z.string().email(),
  personal_email: z.string().email().nullable(),
  first_name: z.string(),
  last_name: z.string(),
  display_name: z.string(),
  profile_picture: z.string().nullable(),
  is_active: z.boolean(),
  roles: z.array(roleSchema),
  primary_role: z
    .enum(["SUPER_ADMIN", "PLACEMENT_CELL", "PLACEMENT_CONVENER", "STUDENT"])
    .nullable(),
  primary_role_label: z.string(),
  workspace_path: z.string().nullable(),
  needs_welcome: z.boolean(),
  last_login: z.string().nullable(),
  created_at: z.string(),
});

export const authTokensSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  user: userSchema,
  is_new_user: z.boolean().default(false),
});

export const messageResponseSchema = z.object({
  message: z.string(),
});

export const apiErrorSchema = z.object({
  message: z.string(),
  error_code: z.string().optional(),
  request_id: z.string().nullable().optional(),
});

export type UserSchema = z.infer<typeof userSchema>;
