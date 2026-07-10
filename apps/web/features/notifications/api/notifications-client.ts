import { apiRequest } from "@/lib/api-client";

export type NotificationItem = {
  id: string;
  recipient_user_id: string;
  type: string;
  title: string;
  message: string;
  entity_type: string | null;
  entity_id: string | null;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
  delivery_status: string;
};

export type NotificationListResponse = {
  items: NotificationItem[];
  total: number;
  unread_count: number;
  page: number;
  page_size: number;
};

export type NotificationPreferences = {
  email_enabled: boolean;
  in_app_enabled: boolean;
};

export async function fetchNotifications(
  page = 1,
  pageSize = 20,
): Promise<NotificationListResponse> {
  return apiRequest<NotificationListResponse>(
    `/notifications?page=${page}&page_size=${pageSize}`,
  );
}

export async function markNotificationRead(
  id: string,
): Promise<{ id: string; is_read: boolean; read_at: string | null }> {
  return apiRequest(`/notifications/${id}/read`, { method: "PATCH" });
}

export async function markAllNotificationsRead(): Promise<{ updated: number }> {
  return apiRequest("/notifications/read-all", { method: "PATCH" });
}

export async function fetchNotificationPreferences(): Promise<NotificationPreferences> {
  return apiRequest("/notifications/preferences");
}

export async function updateNotificationPreferences(
  payload: Partial<NotificationPreferences>,
): Promise<NotificationPreferences> {
  return apiRequest("/notifications/preferences", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
