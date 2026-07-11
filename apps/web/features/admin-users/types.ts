export type UserStatus = "active" | "inactive" | "suspended" | "archived";

export type AdminUserListItem = {
  id: string;
  college_email: string;
  first_name: string;
  last_name: string;
  display_name: string;
  profile_picture: string | null;
  status: UserStatus | string;
  is_active: boolean;
  roles: { id: string; name: string; description: string }[];
  primary_role: string | null;
  department_name: string | null;
  department_code: string | null;
  roll_number: string | null;
  registration_number: string | null;
  verification_status: string | null;
  graduation_year: number | null;
  last_login: string | null;
  created_at: string;
};

export type AdminUserListResponse = {
  items: AdminUserListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export type AdminUserDetail = AdminUserListItem & {
  personal_email: string | null;
  email_verified: boolean;
  role_assignments: {
    role_id: string;
    role_name: string;
    is_primary: boolean;
  }[];
  profile_status: string | null;
  student_profile_id: string | null;
  updated_at: string;
  role_history: {
    id: string;
    role_name: string;
    action: string;
    performed_by: string;
    is_primary: boolean;
    created_at: string;
  }[];
  statistics: Record<string, number | string | null>;
  current_sessions: unknown[];
};

export type AdminAuditItem = {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  performed_by: string;
  performed_at: string;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  metadata: Record<string, unknown> | null;
};

export type AdminUserFilters = {
  search: string;
  role: string;
  status: string;
  departmentId: string;
  verification: string;
  graduationYear: string;
  sortBy: string;
  sortOrder: "asc" | "desc";
  page: number;
  pageSize: number;
};

export const DEFAULT_ADMIN_FILTERS: AdminUserFilters = {
  search: "",
  role: "",
  status: "",
  departmentId: "",
  verification: "",
  graduationYear: "",
  sortBy: "created_at",
  sortOrder: "desc",
  page: 1,
  pageSize: 20,
};

export const ROLE_OPTIONS = [
  "STUDENT",
  "PLACEMENT_CONVENER",
  "PLACEMENT_CELL",
  "SUPER_ADMIN",
] as const;

export const STATUS_OPTIONS = [
  "active",
  "inactive",
  "suspended",
  "archived",
] as const;
