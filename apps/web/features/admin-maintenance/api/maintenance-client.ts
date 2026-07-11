import { apiRequest } from "@/lib/api-client";

export type MaintenanceStatus = {
  enabled: boolean;
  title: string;
  message: string;
  estimated_completion: string | null;
  support_contact: string | null;
  starts_at: string | null;
  ends_at: string | null;
  allowed_roles?: string[];
  updated_by?: string | null;
};

export async function fetchPublicMaintenanceStatus(): Promise<MaintenanceStatus> {
  return apiRequest("/maintenance/status");
}

export async function fetchAdminMaintenance(): Promise<MaintenanceStatus> {
  return apiRequest("/admin/maintenance");
}

export async function patchAdminMaintenance(payload: {
  enabled?: boolean;
  title?: string;
  message?: string;
  estimated_completion?: string | null;
  support_contact?: string | null;
  starts_at?: string | null;
  ends_at?: string | null;
  allowed_roles?: string[];
  confirm: boolean;
}): Promise<MaintenanceStatus> {
  return apiRequest("/admin/maintenance", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
