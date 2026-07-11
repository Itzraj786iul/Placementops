import { apiRequest } from "@/lib/api-client";

export type AdminDepartment = {
  id: string;
  name: string;
  code: string;
  description: string | null;
  display_order: number;
  status: string;
  logo_url: string | null;
  created_at: string;
  updated_at: string;
  archived_at: string | null;
  student_count: number;
  convener_count: number;
  company_count: number;
};

export type AdminSeason = {
  id: string;
  name: string;
  academic_batch: string;
  start_date: string;
  end_date: string;
  status: string;
  is_current: boolean;
  description: string | null;
  created_at: string;
  updated_at: string;
  read_only: boolean;
  stats: {
    applications: number;
    companies: number;
    students: number;
    offers: number;
  } | null;
};

export type Paginated<T> = {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
};

export async function fetchAdminDepartments(params: {
  search?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}): Promise<Paginated<AdminDepartment>> {
  const q = new URLSearchParams();
  q.set("page", String(params.page ?? 1));
  q.set("page_size", String(params.pageSize ?? 20));
  if (params.search) q.set("search", params.search);
  if (params.status) q.set("status", params.status);
  return apiRequest(`/admin/departments?${q}`);
}

export async function createAdminDepartment(payload: {
  name: string;
  code: string;
  description?: string;
  display_order?: number;
}): Promise<AdminDepartment> {
  return apiRequest("/admin/departments", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAdminDepartment(
  id: string,
  payload: Partial<{
    name: string;
    code: string;
    description: string | null;
    display_order: number;
    status: string;
    logo_url: string | null;
  }>,
): Promise<AdminDepartment> {
  return apiRequest(`/admin/departments/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function fetchAdminSeasons(params: {
  search?: string;
  status?: string;
  page?: number;
  pageSize?: number;
}): Promise<Paginated<AdminSeason>> {
  const q = new URLSearchParams();
  q.set("page", String(params.page ?? 1));
  q.set("page_size", String(params.pageSize ?? 20));
  if (params.search) q.set("search", params.search);
  if (params.status) q.set("status", params.status);
  return apiRequest(`/admin/seasons?${q}`);
}

export async function createAdminSeason(payload: {
  name: string;
  academic_batch: string;
  start_date: string;
  end_date: string;
  status?: string;
  description?: string;
}): Promise<AdminSeason> {
  return apiRequest("/admin/seasons", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function updateAdminSeason(
  id: string,
  payload: Partial<{
    name: string;
    academic_batch: string;
    start_date: string;
    end_date: string;
    status: string;
    description: string | null;
  }>,
): Promise<AdminSeason> {
  return apiRequest(`/admin/seasons/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function activateAdminSeason(id: string): Promise<AdminSeason> {
  return apiRequest(`/admin/seasons/${id}/activate`, {
    method: "POST",
    body: JSON.stringify({ confirm: true }),
  });
}
