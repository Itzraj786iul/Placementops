"use client";

import { GraduationCap, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";
import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { getWorkspacePathForUser } from "@/lib/auth/redirects";
import { useAuth } from "@/providers/auth-provider";
import { AuthApiError, completeWelcome } from "@/services/auth-client";

export default function WelcomePage() {
  const { user, isLoading, refreshUser, isAuthenticated } = useAuth();
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  React.useEffect(() => {
    if (isLoading) return;
    if (!isAuthenticated || !user) {
      router.replace("/login");
      return;
    }
    if (!user.needs_welcome) {
      router.replace(getWorkspacePathForUser(user) ?? "/account-inactive");
    }
  }, [isLoading, isAuthenticated, user, router]);

  const handleContinue = async () => {
    setIsSubmitting(true);
    try {
      const updated = await completeWelcome();
      await refreshUser();
      router.replace(getWorkspacePathForUser(updated) ?? "/account-inactive");
    } catch (error) {
      toast.error(
        error instanceof AuthApiError
          ? error.message
          : "Unable to continue. Please try again.",
      );
      setIsSubmitting(false);
    }
  };

  if (isLoading || !user || !user.needs_welcome) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="text-primary h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center px-4">
      <div
        aria-hidden
        className="via-background to-background pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-100 dark:from-emerald-950/30"
      />
      <div className="bg-card relative w-full max-w-md space-y-6 rounded-xl border p-8 shadow-sm">
        <div className="flex flex-col items-center text-center">
          <GraduationCap className="text-primary h-10 w-10" />
          <h1 className="mt-4 text-2xl font-semibold tracking-tight">
            Welcome to PlacementOS
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            Your account has been created successfully.
          </p>
        </div>

        <dl className="space-y-4 rounded-lg border p-4 text-sm">
          <div>
            <dt className="text-muted-foreground">Role</dt>
            <dd className="mt-1 font-medium">
              {user.primary_role_label || "Student"}
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Next step</dt>
            <dd className="mt-1 font-medium">
              Complete your placement profile once. You&apos;ll use this profile
              for every placement opportunity.
            </dd>
          </div>
        </dl>

        <Button
          type="button"
          className="w-full"
          onClick={handleContinue}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Continuing…
            </>
          ) : (
            "Continue"
          )}
        </Button>
      </div>
    </div>
  );
}
