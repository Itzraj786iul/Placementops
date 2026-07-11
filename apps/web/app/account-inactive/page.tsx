"use client";

import { ShieldAlert } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { useAuth } from "@/providers/auth-provider";

type AccountInactivePageProps = {
  searchParams: Promise<{ message?: string }>;
};

export default function AccountInactivePage({
  searchParams,
}: AccountInactivePageProps) {
  const params = React.use(searchParams);
  const { signOut, isAuthenticated } = useAuth();
  const message =
    params.message?.replace(/\+/g, " ") ||
    "Your account is currently inactive. Please contact the Placement Cell.";

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="bg-card w-full max-w-md space-y-6 rounded-xl border p-8 text-center shadow-sm">
        <ShieldAlert className="text-destructive mx-auto h-10 w-10" />
        <div className="space-y-2">
          <h1 className="text-xl font-semibold tracking-tight">
            Account inactive
          </h1>
          <p className="text-muted-foreground text-sm">{message}</p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:justify-center">
          {isAuthenticated && (
            <Button
              type="button"
              variant="outline"
              onClick={() => void signOut()}
            >
              Sign out
            </Button>
          )}
          <Button asChild>
            <Link href="/">Back to home</Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
