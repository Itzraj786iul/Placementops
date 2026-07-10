"use client";

import * as React from "react";
import { toast } from "sonner";

import { LoginErrorAlert } from "@/components/auth/login-error-alert";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getWorkspacePathForUser } from "@/lib/auth/redirects";
import { AuthApiError, devLogin } from "@/services/auth-client";

type DevLoginFormProps = {
  redirectTo?: string;
};

export function DevLoginForm({ redirectTo }: DevLoginFormProps) {
  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [error, setError] = React.useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const tokens = await devLogin(email.trim(), password);
      const path = redirectTo ?? getWorkspacePathForUser(tokens.user);
      // Full page navigation ensures auth cookies are loaded before protected routes render.
      window.location.assign(path);
      return;
    } catch (err) {
      const message =
        err instanceof AuthApiError
          ? err.message
          : "Unable to sign in. Please try again.";
      setError(message);
      toast.error(message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="space-y-4">
      <div className="text-center">
        <p className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
          Development login
        </p>
        <p className="text-muted-foreground mt-1 text-xs">
          Local testing only — not available in production
        </p>
      </div>

      {error && <LoginErrorAlert message={error} />}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="dev-email">Email</Label>
          <Input
            id="dev-email"
            type="email"
            autoComplete="username"
            placeholder="admin@nitrr.ac.in"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="dev-password">Password</Label>
          <Input
            id="dev-password"
            type="password"
            autoComplete="current-password"
            placeholder="Password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
          />
        </div>
        <Button type="submit" className="w-full" disabled={isSubmitting}>
          {isSubmitting ? "Signing in..." : "Sign in with password"}
        </Button>
      </form>
    </div>
  );
}
