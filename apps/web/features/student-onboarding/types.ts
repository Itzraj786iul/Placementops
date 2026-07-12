export type ProfileStatus =
  "DRAFT" | "SUBMITTED" | "UNDER_REVIEW" | "VERIFIED" | "REJECTED";

export type DocumentStatus = "PENDING" | "VERIFIED" | "REJECTED";

export type EducationType =
  "SECONDARY" | "HIGHER_SECONDARY" | "DIPLOMA" | "UNDERGRADUATE";

export type Gender = "MALE" | "FEMALE" | "OTHER";

export type DocumentType =
  | "PHOTO"
  | "AADHAR"
  | "PAN"
  | "TENTH_MARKSHEET"
  | "TWELFTH_MARKSHEET"
  | "SEMESTER_MARKSHEET"
  | "RESUME"
  | "OTHER";

export type VerificationStatus = "PENDING" | "VERIFIED" | "REJECTED";

export type Department = {
  id: string;
  name: string;
  code: string;
};

export type MissingRequirement = {
  code: string;
  label: string;
  step: string;
  focus?: string | null;
  estimated_minutes?: number;
};

export type StudentProfile = {
  id: string;
  user_id: string;
  department_id: string;
  roll_number: string;
  registration_number: string;
  graduation_year: number;
  profile_status: ProfileStatus;
  profile_completion: number;
  missing_requirements?: MissingRequirement[];
  requirements_completed?: number;
  requirements_total?: number;
  optional_completed?: number;
  optional_total?: number;
  optional_missing?: MissingRequirement[];
  estimated_minutes_remaining?: number;
  created_at: string;
  updated_at: string;
  department?: Department | null;
};

export type PersonalInformation = {
  student_profile_id: string;
  first_name: string;
  last_name: string;
  gender: Gender;
  date_of_birth: string;
  phone_number: string;
  alternate_phone: string | null;
  personal_email: string | null;
  address: string;
  city: string;
  state: string;
  country: string;
  photo_url: string | null;
};

export type AcademicInformation = {
  student_profile_id: string;
  current_cgpa: string;
  active_backlogs: number;
  total_history_backlogs: number;
  semester: number;
};

export type EducationRecord = {
  id: string;
  student_profile_id: string;
  education_type: EducationType;
  institution: string;
  board: string;
  passing_year: number;
  percentage_or_cgpa: string;
};

export type Resume = {
  id: string;
  student_profile_id: string;
  name: string;
  file_url: string;
  version: number;
  is_active: boolean;
  last_used: string | null;
  uploaded_at: string;
};

export type StudentDocument = {
  id: string;
  student_profile_id: string;
  document_type: DocumentType;
  file_url: string;
  file_name: string;
  status: DocumentStatus;
  uploaded_at: string;
};

export type Skill = {
  id: string;
  student_profile_id: string;
  skill_name: string;
  skill_level: string;
};

export type Project = {
  id: string;
  student_profile_id: string;
  title: string;
  description: string;
  tech_stack: string;
  github_url: string | null;
  demo_url: string | null;
};

export type Verification = {
  student_profile_id: string;
  personal_status: VerificationStatus;
  academic_status: VerificationStatus;
  documents_status: VerificationStatus;
  resume_status: VerificationStatus;
  overall_status: VerificationStatus;
  reviewer_id: string | null;
  remarks: string | null;
  reviewed_at: string | null;
};
