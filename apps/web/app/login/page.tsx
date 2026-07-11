"use client";

import { Eye, EyeOff, GraduationCap, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { toast } from "sonner";

import { GoogleSignInButton } from "@/components/auth/google-sign-in-button";
import { LoginErrorAlert } from "@/components/auth/login-error-alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { getPostAuthPath } from "@/lib/auth/redirects";
import { useAuth } from "@/providers/auth-provider";
import { AuthApiError, passwordLogin } from "@/services/auth-client";

type LoginPageProps = {
  searchParams: Promise<{ error?: string; redirect?: string }>;
};

export default function LoginPage({ searchParams }: LoginPageProps) {
  const params = React.use(searchParams);
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [rememberMe, setRememberMe] = React.useState(true);
  const [showPassword, setShowPassword] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

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

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const tokens = await passwordLogin({
        email: email.trim(),
        password,
        remember_me: rememberMe,
      });
      window.location.assign(getPostAuthPath(tokens.user, tokens.is_new_user));
    } catch (err) {
      const message =
        err instanceof AuthApiError
          ? err.message
          : "Unable to sign in. Please try again.";
      setError(message);
      toast.error(message);
      setIsSubmitting(false);
    }
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
          <h1 className="mt-6 text-2xl font-semibold tracking-tight">
            Welcome back
          </h1>
          <p className="text-muted-foreground mt-2 text-sm">
            Sign in with your NIT Raipur account
          </p>
        </div>

        {(params.error || error) && (
          <LoginErrorAlert message={error ?? params.error!} />
        )}

        <div className="bg-card/90 rounded-xl border p-8 shadow-sm backdrop-blur">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                autoComplete="username"
                placeholder="name@nitrr.ac.in"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password">Password</Label>
                <Link
                  href="/forgot-password"
                  className="text-primary text-xs underline-offset-2 hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  autoComplete="current-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="pr-10"
                />
                <button
                  type="button"
                  className="text-muted-foreground absolute top-1/2 right-3 -translate-y-1/2"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="accent-primary h-4 w-4"
              />
              Remember me
            </label>
            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Signing in…
                </>
              ) : (
                "Sign in"
              )}
            </Button>
          </form>

          <div className="my-6 flex items-center gap-3">
            <Separator className="flex-1" />
            <span className="text-muted-foreground text-xs">OR</span>
            <Separator className="flex-1" />
          </div>

          <GoogleSignInButton className="w-full" />

          <p className="text-muted-foreground mt-6 text-center text-xs">
            Only @nitrr.ac.in accounts are allowed. Students, conveners, and
            staff use this same sign-in page.
          </p>
        </div>

        <p className="text-muted-foreground text-center text-sm">
          New student?{" "}
          <Link href="/register" className="underline-offset-4 hover:underline">
            Create an account
          </Link>
          {" · "}
          <Link href="/" className="underline-offset-4 hover:underline">
            Home
          </Link>
        </p>
      </div>
    </div>
  );
}
