"use client";

import { Eye, EyeOff, Loader2 } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { AuthApiError, resetPassword } from "@/services/auth-client";

type Props = { searchParams: Promise<{ token?: string }> };

export default function ResetPasswordPage({ searchParams }: Props) {
  const params = React.use(searchParams);
  const router = useRouter();
  const [password, setPassword] = React.useState("");
  const [confirm, setConfirm] = React.useState("");
  const [show, setShow] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!params.token) {
      toast.error("Reset link is missing or invalid");
      return;
    }
    if (password !== confirm) {
      toast.error("Passwords do not match");
      return;
    }
    setIsSubmitting(true);
    try {
      await resetPassword(params.token, password);
      toast.success("Password updated. Please sign in.");
      router.replace("/login");
    } catch (err) {
      toast.error(
        err instanceof AuthApiError ? err.message : "Unable to reset password",
      );
      setIsSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="bg-card w-full max-w-md space-y-6 rounded-xl border p-8 shadow-sm">
        <h1 className="text-xl font-semibold">Set a new password</h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="password">New password</Label>
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
              "Update password"
            )}
          </Button>
        </form>
        <Link href="/login" className="text-muted-foreground text-sm underline">
          Back to sign in
        </Link>
      </div>
    </div>
  );
}
