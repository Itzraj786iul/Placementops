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
  profile_picture: z.string().nullable(),
  is_active: z.boolean(),
  roles: z.array(roleSchema),
  last_login: z.string().nullable(),
  created_at: z.string(),
});

export const authTokensSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
  user: userSchema,
});

export const messageResponseSchema = z.object({
  message: z.string(),
});

export const apiErrorSchema = z.object({
  message: z.string(),
});

export type UserSchema = z.infer<typeof userSchema>;
