"use client";

import {
  Briefcase,
  Building2,
  GraduationCap,
  Menu,
  Shield,
  Users,
  X,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { hasAnyRole } from "@/lib/auth/roles";
import { APP_NAME } from "@/lib/constants";
import { NAV_ITEMS } from "@/lib/navigation";
import { useAuth } from "@/providers/auth-provider";
import { cn } from "@/lib/utils";

const iconMap = {
  GraduationCap,
  Briefcase,
  Users,
  Building2,
  Shield,
} as const;

interface AppSidebarProps {
  isOpen: boolean;
  onClose: () => void;
}

export function AppSidebar({ isOpen, onClose }: AppSidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();

  const visibleItems = NAV_ITEMS.filter((item) =>
    hasAnyRole(user, [...item.roles]),
  );

  return (
    <>
      {isOpen && (
        <div
          className="bg-background/80 fixed inset-0 z-40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          "border-sidebar-border bg-sidebar text-sidebar-foreground fixed inset-y-0 left-0 z-50 flex w-64 flex-col border-r transition-transform duration-200 ease-in-out lg:static lg:translate-x-0",
          isOpen ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-14 items-center justify-between px-4 lg:justify-start">
          <Link
            href="/"
            className="flex items-center gap-2 font-semibold"
            onClick={onClose}
          >
            <GraduationCap className="text-sidebar-primary h-6 w-6" />
            <span>{APP_NAME}</span>
          </Link>
          <Button
            variant="ghost"
            size="icon"
            className="lg:hidden"
            onClick={onClose}
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>

        <Separator />

        <nav className="flex-1 space-y-1 p-4">
          {visibleItems.map((item) => {
            const Icon = iconMap[item.icon as keyof typeof iconMap];
            const isActive = pathname === item.href;

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onClose}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-sidebar-accent text-sidebar-accent-foreground"
                    : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                )}
              >
                <Icon className="h-4 w-4" />
                {item.title}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}

export function SidebarToggle({ onOpen }: { onOpen: () => void }) {
  return (
    <Button
      variant="ghost"
      size="icon"
      className="lg:hidden"
      onClick={onOpen}
      aria-label="Open sidebar"
    >
      <Menu className="h-5 w-5" />
    </Button>
  );
}
