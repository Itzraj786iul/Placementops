import { apiRequest } from "@/lib/api-client";
import type {
  AdminAuditItem,
  AdminUserDetail,
  AdminUserFilters,
  AdminUserListItem,
  AdminUserListResponse,
} from "@/features/admin-users/types";

function buildQuery(filters: AdminUserFilters): string {
  const params = new URLSearchParams();
  params.set("page", String(filters.page));
  params.set("page_size", String(filters.pageSize));
  params.set("sort_by", filters.sortBy);
  params.set("sort_order", filters.sortOrder);
  if (filters.search.trim()) params.set("search", filters.search.trim());
  if (filters.role) params.set("role", filters.role);
  if (filters.status) params.set("status", filters.status);
  if (filters.departmentId) params.set("department_id", filters.departmentId);
  if (filters.verification) params.set("verification", filters.verification);
  if (filters.graduationYear) {
    params.set("graduation_year", filters.graduationYear);
  }
  return params.toString();
}

export async function fetchAdminUsers(
  filters: AdminUserFilters,
): Promise<AdminUserListResponse> {
  return apiRequest<AdminUserListResponse>(
    `/admin/users?${buildQuery(filters)}`,
  );
}

export async function fetchAdminUser(id: string): Promise<AdminUserDetail> {
  return apiRequest<AdminUserDetail>(`/admin/users/${id}`);
}

export async function updateAdminUser(
  id: string,
  payload: {
    status?: string;
    first_name?: string;
    last_name?: string;
    display_name?: string;
  },
): Promise<AdminUserDetail> {
  return apiRequest<AdminUserDetail>(`/admin/users/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function updateAdminUserRoles(
  id: string,
  payload: {
    assign?: string[];
    remove?: string[];
    primary_role?: string | null;
  },
): Promise<AdminUserDetail> {
  return apiRequest<AdminUserDetail>(`/admin/users/${id}/roles`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function bulkUpdateAdminUsers(payload: {
  user_ids: string[];
  action: "activate" | "deactivate" | "assign_role" | "export";
  role_name?: string;
  confirm: boolean;
}): Promise<{
  updated: number;
  skipped: number;
  export_rows: AdminUserListItem[] | null;
}> {
  return apiRequest(`/admin/users/bulk`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchAdminUserAudit(
  id: string,
): Promise<{ items: AdminAuditItem[]; total: number }> {
  return apiRequest(`/admin/users/${id}/audit`);
}
