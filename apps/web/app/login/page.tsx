import { GraduationCap } from "lucide-react";
import Link from "next/link";

import { DevLoginForm } from "@/components/auth/dev-login-form";
import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { LoginErrorAlert } from "@/components/auth/login-error-alert";
import { Separator } from "@/components/ui/separator";

type LoginPageProps = {
  searchParams: Promise<{ error?: string; redirect?: string }>;
};

const devLoginEnabled =
  process.env.NODE_ENV === "development" ||
  process.env.NEXT_PUBLIC_ENABLE_DEV_LOGIN === "true";

export default async function LoginPage({ searchParams }: LoginPageProps) {
  const params = await searchParams;

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-2 font-semibold"
          >
            <GraduationCap className="text-primary h-8 w-8" />
            <span className="text-xl">PlacementOS</span>
          </Link>
          <h1 className="mt-6 text-2xl font-semibold tracking-tight">
            Sign in to your account
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            {devLoginEnabled
              ? "Use a dev account below or your NITRR Google account"
              : "Use your NITRR Google account (@nitrr.ac.in or @dept.nitrr.ac.in)"}
          </p>
        </div>

        {params.error && <LoginErrorAlert message={params.error} />}

        <div className="bg-card rounded-lg border p-8 shadow-sm">
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

          <GoogleSignInButton className="w-full" mode="signin" />
          <p className="text-muted-foreground mt-4 text-center text-xs">
            Only NITRR institutional emails (@nitrr.ac.in or department
            addresses like @mme.nitrr.ac.in) are permitted.
          </p>
        </div>

        <p className="text-muted-foreground text-center text-sm">
          New student?{" "}
          <Link href="/signup" className="underline-offset-4 hover:underline">
            Sign up
          </Link>
          {" · "}
          <Link href="/" className="underline-offset-4 hover:underline">
            Back to home
          </Link>
        </p>
      </div>
    </div>
  );
}
