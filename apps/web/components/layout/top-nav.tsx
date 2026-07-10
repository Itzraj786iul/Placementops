"use client";

import { NotificationButton } from "@/components/layout/notification-button";
import { ProfileMenu } from "@/components/layout/profile-menu";
import { SidebarToggle } from "@/components/layout/app-sidebar";
import { ThemeToggle } from "@/components/layout/theme-toggle";
import { Separator } from "@/components/ui/separator";

interface TopNavProps {
  onSidebarOpen: () => void;
}

export function TopNav({ onSidebarOpen }: TopNavProps) {
  return (
    <header className="bg-background sticky top-0 z-30 flex h-14 items-center gap-4 border-b px-4">
      <SidebarToggle onOpen={onSidebarOpen} />

      <div className="flex flex-1 items-center justify-end gap-2">
        <NotificationButton />
        <ThemeToggle />
        <Separator orientation="vertical" className="h-6" />
        <ProfileMenu />
      </div>
    </header>
  );
}
