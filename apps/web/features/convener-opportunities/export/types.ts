export type ExportFormat = "csv" | "xlsx";

export type ExportScope = "all" | "eligible" | "ineligible";

export type ExportColumn =
  | "roll_number"
  | "registration_number"
  | "student_name"
  | "department"
  | "department_code"
  | "cgpa"
  | "active_backlogs"
  | "history_backlogs"
  | "graduation_year"
  | "gender"
  | "personal_email"
  | "phone_number"
  | "resume_used"
  | "application_status"
  | "applied_at"
  | "eligibility"
  | "company";

export type ExportFilters = {
  status?: string[] | null;
  department?: string | null;
  company_id?: string | null;
};

export type ExportRequest = {
  format: ExportFormat;
  scope: ExportScope;
  columns: ExportColumn[];
  filters: ExportFilters;
};

export const EXPORT_COLUMN_OPTIONS: { value: ExportColumn; label: string }[] = [
  { value: "roll_number", label: "Roll Number" },
  { value: "registration_number", label: "Registration Number" },
  { value: "student_name", label: "Student Name" },
  { value: "department", label: "Department" },
  { value: "department_code", label: "Department Code" },
  { value: "cgpa", label: "CGPA" },
  { value: "active_backlogs", label: "Active Backlogs" },
  { value: "history_backlogs", label: "History Backlogs" },
  { value: "graduation_year", label: "Graduation Year" },
  { value: "gender", label: "Gender" },
  { value: "personal_email", label: "Personal Email" },
  { value: "phone_number", label: "Phone Number" },
  { value: "resume_used", label: "Resume Used" },
  { value: "application_status", label: "Application Status" },
  { value: "applied_at", label: "Applied At" },
  { value: "eligibility", label: "Eligibility" },
  { value: "company", label: "Company" },
];

export const DEFAULT_EXPORT_COLUMNS: ExportColumn[] = [
  "roll_number",
  "registration_number",
  "student_name",
  "department",
  "cgpa",
  "active_backlogs",
  "history_backlogs",
  "graduation_year",
  "resume_used",
  "application_status",
  "applied_at",
];

export const EXPORT_COLUMNS_STORAGE_KEY = "placementos.export.columns";
