"use client";

import { GraduationCap, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";

import { DevLoginForm } from "@/components/auth/dev-login-form";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { LoginErrorAlert } from "@/components/auth/login-error-alert";
import { Separator } from "@/components/ui/separator";
import { getPostAuthPath } from "@/lib/auth/redirects";
import { useAuth } from "@/providers/auth-provider";

const devLoginEnabled =
  process.env.NODE_ENV === "development" ||
  process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN === "true";

type LoginPageProps = {
  searchParams: Promise<{ error?: string; redirect?: string }>;
};

export default function LoginPage({ searchParams }: LoginPageProps) {
  const params = React.use(searchParams);
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  React.useEffect(() => {
    if (isLoading || !isAuthenticated || !user) return;
    router.replace(getPostAuthPath(user));
  }, [isLoading, isAuthenticated, user, router]);

  if (isLoading || (isAuthenticated && user)) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center px-4">
        <Loader2 className="text-primary h-8 w-8 animate-spin" />
        <p className="text-muted-foreground mt-4 text-sm">
          Taking you to your workspace…
        </p>
      </div>
    );
  }

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden px-4">
      <div
        aria-hidden
        className="via-background to-background pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-sky-100 dark:from-sky-950/40"
      />
      <div className="relative w-full max-w-md space-y-8">
        <div className="text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 font-semibold tracking-tight"
          >
            <GraduationCap className="text-primary h-9 w-9" />
            <span className="text-2xl">PlacementOS</span>
          </Link>
          <p className="text-muted-foreground mt-3 text-sm font-medium">
            Campus Recruitment Management System
          </p>
          <p className="text-muted-foreground mt-1 text-xs">
            National Institute of Technology, Raipur
          </p>
        </div>

        {params.error && <LoginErrorAlert message={params.error} />}

        <div className="bg-card/90 rounded-xl border p-8 shadow-sm backdrop-blur">
          <div className="mb-6 space-y-2 text-center">
            <h1 className="text-xl font-semibold tracking-tight">
              Sign in with Google
            </h1>
            <p className="text-muted-foreground text-sm">
              Sign in using your official NIT Raipur Google account.
            </p>
            <p className="text-muted-foreground text-xs">
              Only <span className="font-medium">@nitrr.ac.in</span> accounts
              are allowed (including department addresses such as
              @mme.nitrr.ac.in).
            </p>
          </div>

          {devLoginEnabled && (
            <>
              <DevLoginForm redirectTo={params.redirect} />
              <div className="my-6 flex items-center gap-3">
                <Separator className="flex-1" />
                <span className="text-muted-foreground text-xs">or</span>
                <Separator className="flex-1" />
              </div>
            </>
          )}

          <GoogleSignInButton className="w-full" />

          <p className="text-muted-foreground mt-6 text-center text-xs leading-relaxed">
            By continuing, you agree to use PlacementOS for official placement
            activities. We only receive your NITRR Google profile needed to
            create or sign in to your account. Staff roles are assigned by the
            Placement Cell — there is no separate registration.
          </p>
        </div>

        <p className="text-muted-foreground text-center text-sm">
          <Link href="/" className="underline-offset-4 hover:underline">
            Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}
