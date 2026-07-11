import type { ProfileStatus } from "@/features/student-onboarding/types";

export const ONBOARDING_STEPS = [
  { id: "personal", label: "Personal Information", order: 1 },
  { id: "academic", label: "Academic Information", order: 2 },
  { id: "education", label: "Education History", order: 3 },
  { id: "resume", label: "Resume Library", order: 4 },
  { id: "documents", label: "Documents", order: 5 },
  { id: "skills", label: "Skills", order: 6 },
  { id: "projects", label: "Projects", order: 7 },
  { id: "review", label: "Review & Submit", order: 8 },
] as const;

export type OnboardingStepId = (typeof ONBOARDING_STEPS)[number]["id"];

export const EDUCATION_TYPE_LABELS: Record<string, string> = {
  SECONDARY: "Secondary (10th)",
  HIGHER_SECONDARY: "Higher Secondary (12th)",
  DIPLOMA: "Diploma",
  UNDERGRADUATE: "Undergraduate",
};

/** Levels students fill during onboarding (Diploma is not used at NIT Raipur). */
export const ONBOARDING_EDUCATION_TYPES = [
  "SECONDARY",
  "HIGHER_SECONDARY",
  "UNDERGRADUATE",
] as const;

export const NITRR_INSTITUTION_NAME = "National Institute of Technology Raipur";

export const REQUIRED_DOCUMENT_TYPES = [
  "AADHAR",
  "TENTH_MARKSHEET",
  "TWELFTH_MARKSHEET",
] as const;

/** Shown on the Documents step. Photo lives in Personal Information; resumes have their own step. */
export const DOCUMENT_STEP_TYPES = [
  "AADHAR",
  "PAN",
  "TENTH_MARKSHEET",
  "TWELFTH_MARKSHEET",
  "SEMESTER_MARKSHEET",
  "OTHER",
] as const;

export const DOCUMENT_TYPE_LABELS: Record<string, string> = {
  PHOTO: "Photograph",
  AADHAR: "Aadhar Card",
  PAN: "PAN Card",
  TENTH_MARKSHEET: "10th Marksheet",
  TWELFTH_MARKSHEET: "12th Marksheet",
  SEMESTER_MARKSHEET: "Semester Marksheet",
  RESUME: "Resume",
  OTHER: "Other",
};

export const SKILL_SUGGESTIONS = [
  "Python",
  "Java",
  "JavaScript",
  "TypeScript",
  "React",
  "Node.js",
  "SQL",
  "Docker",
  "AWS",
  "C++",
  "Data Structures",
  "Machine Learning",
];

export const SKILL_LEVELS = ["Beginner", "Intermediate", "Advanced", "Expert"];

export const READ_ONLY_STATUSES: ProfileStatus[] = [
  "SUBMITTED",
  "UNDER_REVIEW",
  "VERIFIED",
];

export function isProfileReadOnly(status: ProfileStatus): boolean {
  return READ_ONLY_STATUSES.includes(status);
}

export function canSubmitProfile(completion: number): boolean {
  return completion >= 100;
}
