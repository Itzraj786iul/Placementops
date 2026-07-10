import { z } from "zod";

export const genderSchema = z.enum(["MALE", "FEMALE", "OTHER"]);

export const educationTypeSchema = z.enum([
  "SECONDARY",
  "HIGHER_SECONDARY",
  "DIPLOMA",
  "UNDERGRADUATE",
]);

export const documentTypeSchema = z.enum([
  "PHOTO",
  "AADHAR",
  "PAN",
  "TENTH_MARKSHEET",
  "TWELFTH_MARKSHEET",
  "SEMESTER_MARKSHEET",
  "RESUME",
  "OTHER",
]);

export const profileBootstrapSchema = z.object({
  department_id: z.string().uuid("Select a department"),
  roll_number: z.string().min(1, "Roll number is required").max(50),
  registration_number: z
    .string()
    .min(1, "Registration number is required")
    .max(50),
  graduation_year: z.coerce
    .number()
    .min(2000, "Enter a valid year")
    .max(2100, "Enter a valid year"),
});

export const personalInfoSchema = z.object({
  first_name: z.string().min(1, "First name is required").max(100),
  last_name: z.string().min(1, "Last name is required").max(100),
  gender: genderSchema,
  date_of_birth: z.string().min(1, "Date of birth is required"),
  phone_number: z
    .string()
    .min(10, "Enter a valid phone number")
    .max(20, "Phone number is too long"),
  alternate_phone: z.string().max(20).optional().or(z.literal("")),
  personal_email: z
    .string()
    .email("Enter a valid email")
    .optional()
    .or(z.literal("")),
  address: z.string().min(1, "Address is required"),
  city: z.string().min(1, "City is required").max(100),
  state: z.string().min(1, "State is required").max(100),
  country: z.string().min(1, "Country is required").max(100),
  photo_url: z.string().url("Enter a valid URL").optional().or(z.literal("")),
});

export const academicInfoSchema = z.object({
  current_cgpa: z.coerce
    .number()
    .min(0, "CGPA must be at least 0")
    .max(10, "CGPA cannot exceed 10"),
  semester: z.coerce
    .number()
    .min(1, "Semester must be at least 1")
    .max(12, "Semester cannot exceed 12"),
  active_backlogs: z.coerce.number().min(0, "Cannot be negative"),
  total_history_backlogs: z.coerce.number().min(0, "Cannot be negative"),
});

export const educationRecordSchema = z.object({
  education_type: educationTypeSchema,
  institution: z.string().min(1, "Institution is required").max(255),
  board: z.string().min(1, "Board is required").max(255),
  passing_year: z.coerce
    .number()
    .min(1980, "Enter a valid year")
    .max(2100, "Enter a valid year"),
  percentage_or_cgpa: z.string().min(1, "Result is required").max(20),
});

export const resumeSchema = z.object({
  name: z.string().min(1, "Resume name is required").max(150),
  file_url: z.string().url("Enter a valid file URL"),
  version: z.coerce.number().min(1).default(1),
  is_active: z.boolean().default(false),
});

export const documentUploadSchema = z.object({
  document_type: documentTypeSchema,
  file_url: z.string().url("Enter a valid file URL"),
  file_name: z.string().min(1, "File name is required").max(255),
});

export const skillSchema = z.object({
  skill_name: z.string().min(1, "Skill name is required").max(100),
  skill_level: z.string().min(1, "Skill level is required").max(50),
});

export const projectSchema = z.object({
  title: z.string().min(1, "Title is required").max(200),
  description: z.string().min(1, "Description is required"),
  tech_stack: z.string().min(1, "Technology stack is required").max(500),
  github_url: z.string().url("Enter a valid URL").optional().or(z.literal("")),
  demo_url: z.string().url("Enter a valid URL").optional().or(z.literal("")),
});

export type ProfileBootstrapValues = z.infer<typeof profileBootstrapSchema>;
export type PersonalInfoValues = z.infer<typeof personalInfoSchema>;
export type AcademicInfoValues = z.infer<typeof academicInfoSchema>;
export type EducationRecordValues = z.infer<typeof educationRecordSchema>;
export type ResumeValues = z.infer<typeof resumeSchema>;
export type DocumentUploadValues = z.infer<typeof documentUploadSchema>;
export type SkillValues = z.infer<typeof skillSchema>;
export type ProjectValues = z.infer<typeof projectSchema>;
