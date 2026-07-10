"use client";

import { Bell } from "lucide-react";
import * as React from "react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  useNotificationMutations,
  useNotificationPreferences,
  useNotifications,
} from "@/features/notifications/hooks/use-notifications";
import { cn } from "@/lib/utils";

function formatWhen(iso: string): string {
  const date = new Date(iso);
  const diffMs = Date.now() - date.getTime();
  const mins = Math.floor(diffMs / 60_000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

export function NotificationButton() {
  const [open, setOpen] = React.useState(false);
  const { data, isLoading, isError } = useNotifications();
  const prefs = useNotificationPreferences(open);
  const { markRead, markAllRead, updatePrefs } = useNotificationMutations();

  const unread = data?.unread_count ?? 0;
  const items = data?.items ?? [];

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={
            unread > 0 ? `Notifications (${unread} unread)` : "Notifications"
          }
          className="relative"
        >
          <Bell className="h-4 w-4" />
          {unread > 0 && (
            <span className="bg-destructive text-destructive-foreground absolute top-1.5 right-1.5 flex h-4 min-w-4 items-center justify-center rounded-full px-1 text-[10px] font-medium">
              {unread > 99 ? "99+" : unread}
            </span>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-80 p-0" align="end" forceMount>
        <div className="flex items-center justify-between px-3 py-2">
          <DropdownMenuLabel className="p-0">Notifications</DropdownMenuLabel>
          {unread > 0 && (
            <Button
              type="button"
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              disabled={markAllRead.isPending}
              onClick={() => markAllRead.mutate()}
            >
              Mark all read
            </Button>
          )}
        </div>
        <DropdownMenuSeparator className="m-0" />
        <div className="max-h-80 overflow-y-auto">
          {isLoading && (
            <p className="text-muted-foreground px-3 py-6 text-center text-sm">
              Loading…
            </p>
          )}
          {isError && (
            <p className="text-destructive px-3 py-6 text-center text-sm">
              Failed to load notifications
            </p>
          )}
          {!isLoading && !isError && items.length === 0 && (
            <p className="text-muted-foreground px-3 py-6 text-center text-sm">
              No notifications yet
            </p>
          )}
          {items.map((item) => (
            <DropdownMenuItem
              key={item.id}
              className={cn(
                "flex cursor-pointer flex-col items-start gap-0.5 rounded-none px-3 py-2.5",
                !item.is_read && "bg-muted/50",
              )}
              onSelect={(e) => {
                e.preventDefault();
                if (!item.is_read) markRead.mutate(item.id);
              }}
            >
              <div className="flex w-full items-start justify-between gap-2">
                <p className="text-sm leading-snug font-medium">{item.title}</p>
                {!item.is_read && (
                  <span className="bg-primary mt-1 h-2 w-2 shrink-0 rounded-full" />
                )}
              </div>
              <p className="text-muted-foreground line-clamp-2 text-xs">
                {item.message}
              </p>
              <p className="text-muted-foreground text-[10px]">
                {formatWhen(item.created_at)}
              </p>
            </DropdownMenuItem>
          ))}
        </div>
        <DropdownMenuSeparator className="m-0" />
        <div className="space-y-2 px-3 py-2">
          <p className="text-muted-foreground text-[10px] font-medium tracking-wide uppercase">
            Preferences
          </p>
          <div className="flex items-center justify-between gap-2 text-xs">
            <span>Email</span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7"
              disabled={updatePrefs.isPending || prefs.isLoading}
              onClick={() =>
                updatePrefs.mutate({
                  email_enabled: !(prefs.data?.email_enabled ?? true),
                })
              }
            >
              {prefs.data?.email_enabled === false ? "Off" : "On"}
            </Button>
          </div>
          <div className="flex items-center justify-between gap-2 text-xs">
            <span>In-app</span>
            <Button
              type="button"
              variant="outline"
              size="sm"
              className="h-7"
              disabled={updatePrefs.isPending || prefs.isLoading}
              onClick={() =>
                updatePrefs.mutate({
                  in_app_enabled: !(prefs.data?.in_app_enabled ?? true),
                })
              }
            >
              {prefs.data?.in_app_enabled === false ? "Off" : "On"}
            </Button>
          </div>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
