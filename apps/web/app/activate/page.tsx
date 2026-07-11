"use client";

import { Eye, EyeOff, Loader2 } from "lucide-react";
import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { getPostAuthPath } from "@/lib/auth/redirects";
import { AuthApiError, activateAccount } from "@/services/auth-client";

type Props = { searchParams: Promise<{ token?: string }> };

export default function ActivatePage({ searchParams }: Props) {
  const params = React.use(searchParams);
  const [password, setPassword] = React.useState("");
  const [confirm, setConfirm] = React.useState("");
  const [show, setShow] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!params.token) {
      toast.error("Activation link is missing");
      return;
    }
    setIsSubmitting(true);
    try {
      const tokens = await activateAccount({
        token: params.token,
        password,
        confirm_password: confirm,
      });
      window.location.assign(getPostAuthPath(tokens.user, tokens.is_new_user));
    } catch (err) {
      toast.error(
        err instanceof AuthApiError
          ? err.message
          : "Unable to activate account",
      );
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="bg-card w-full max-w-md space-y-6 rounded-xl border p-8 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold">Activate your account</h1>
          <p className="text-muted-foreground mt-2 text-sm">
            Create a password to finish setting up your PlacementOS account.
          </p>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={show ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                className="pr-10"
              />
              <button
                type="button"
                className="text-muted-foreground absolute top-1/2 right-3 -translate-y-1/2"
                onClick={() => setShow((v) => !v)}
              >
                {show ? (
                  <EyeOff className="h-4 w-4" />
                ) : (
                  <Eye className="h-4 w-4" />
                )}
              </button>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="confirm">Confirm password</Label>
            <Input
              id="confirm"
              type={show ? "text" : "password"}
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={8}
            />
          </div>
          <Button type="submit" className="w-full" disabled={isSubmitting}>
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Activate and sign in"
            )}
          </Button>
        </form>
      </div>
    </div>
  );
}
