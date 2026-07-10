"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
  fetchNotificationPreferences,
  fetchNotifications,
  markAllNotificationsRead,
  markNotificationRead,
  updateNotificationPreferences,
  type NotificationPreferences,
} from "@/features/notifications/api/notifications-client";
import { useAuth } from "@/providers/auth-provider";

export const notificationKeys = {
  all: ["notifications"] as const,
  list: () => [...notificationKeys.all, "list"] as const,
  preferences: () => [...notificationKeys.all, "preferences"] as const,
};

export function useNotifications(enabled = true) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: notificationKeys.list(),
    queryFn: () => fetchNotifications(1, 20),
    enabled: enabled && isAuthenticated,
    refetchInterval: 60_000,
  });
}

export function useNotificationPreferences(enabled = true) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: notificationKeys.preferences(),
    queryFn: fetchNotificationPreferences,
    enabled: enabled && isAuthenticated,
  });
}

export function useNotificationMutations() {
  const queryClient = useQueryClient();

  const invalidate = () =>
    queryClient.invalidateQueries({ queryKey: notificationKeys.all });

  const markRead = useMutation({
    mutationFn: markNotificationRead,
    onSuccess: () => void invalidate(),
  });

  const markAllRead = useMutation({
    mutationFn: markAllNotificationsRead,
    onSuccess: () => void invalidate(),
  });

  const updatePrefs = useMutation({
    mutationFn: (payload: Partial<NotificationPreferences>) =>
      updateNotificationPreferences(payload),
    onSuccess: () => void invalidate(),
  });

  return { markRead, markAllRead, updatePrefs };
}
