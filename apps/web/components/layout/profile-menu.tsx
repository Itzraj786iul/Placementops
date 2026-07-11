"use client";

import { KeyRound, LogOut, User } from "lucide-react";
import Link from "next/link";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { getUserDisplayName, getUserInitials } from "@/lib/auth/roles";
import { useAuth } from "@/providers/auth-provider";

export function ProfileMenu() {
  const { user, isLoading, signOut } = useAuth();

  if (isLoading || !user) {
    return (
      <Button
        variant="ghost"
        className="relative h-9 w-9 rounded-full"
        aria-label="Profile menu"
        disabled
      >
        <Avatar className="h-9 w-9">
          <AvatarFallback className="text-xs">--</AvatarFallback>
        </Avatar>
      </Button>
    );
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="ghost"
          className="relative h-9 w-9 rounded-full"
          aria-label="Profile menu"
        >
          <Avatar className="h-9 w-9">
            {user.profile_picture && (
              <AvatarImage
                src={user.profile_picture}
                alt={getUserDisplayName(user)}
              />
            )}
            <AvatarFallback className="text-xs">
              {getUserInitials(user)}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm leading-none font-medium">
              {getUserDisplayName(user)}
            </p>
            <p className="text-muted-foreground text-xs leading-none">
              {user.college_email}
            </p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem disabled>
          <User className="mr-2 h-4 w-4" />
          Profile
        </DropdownMenuItem>
        <DropdownMenuItem asChild>
          <Link href="/workspace/account/security">
            <KeyRound className="mr-2 h-4 w-4" />
            Security
          </Link>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => void signOut()}>
          <LogOut className="mr-2 h-4 w-4" />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
