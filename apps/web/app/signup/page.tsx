import { GraduationCap } from "lucide-react";
import Link from "next/link";

import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { LoginErrorAlert } from "@/components/auth/login-error-alert";

type SignupPageProps = {
  searchParams: Promise<{ error?: string }>;
};

export default async function SignupPage({ searchParams }: SignupPageProps) {
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
            Create your account
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            Sign up with your NITRR Google account (@nitrr.ac.in). New students
            are registered automatically on first Google sign-in.
          </p>
        </div>

        {params.error && <LoginErrorAlert message={params.error} />}

        <div className="bg-card rounded-lg border p-8 shadow-sm">
          <GoogleSignInButton className="w-full" mode="signup" />
          <p className="text-muted-foreground mt-4 text-center text-xs">
            Only institutional email addresses ending with @nitrr.ac.in are
            permitted. Staff roles are assigned by administrators.
          </p>
        </div>

        <p className="text-muted-foreground text-center text-sm">
          Already have an account?{" "}
          <Link href="/login" className="underline-offset-4 hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
