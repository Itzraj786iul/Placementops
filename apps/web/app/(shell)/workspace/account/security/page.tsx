"use client";

import { Eye, EyeOff, Loader2 } from "lucide-react";
import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ProtectedRoute } from "@/components/auth/protected-route";
import { useAuth } from "@/providers/auth-provider";
import {
  AuthApiError,
  changePassword,
  createPassword,
} from "@/services/auth-client";

function SecurityForm() {
  const { user, refreshUser } = useAuth();
  const [currentPassword, setCurrentPassword] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [confirm, setConfirm] = React.useState("");
  const [show, setShow] = React.useState(false);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  if (!user) return null;

  const hasPassword = user.has_password;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      if (hasPassword) {
        await changePassword({
          current_password: currentPassword,
          new_password: password,
          confirm_password: confirm,
        });
        toast.success("Password changed");
      } else {
        await createPassword(password, confirm);
        toast.success("Password created — you can now sign in with email");
      }
      setCurrentPassword("");
      setPassword("");
      setConfirm("");
      await refreshUser();
    } catch (err) {
      toast.error(
        err instanceof AuthApiError ? err.message : "Unable to update password",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="mx-auto max-w-lg space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Security</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          {hasPassword
            ? "Change your password. Google sign-in remains available."
            : "Create a password so you can also sign in with email."}
        </p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-4 rounded-xl border p-6">
        {hasPassword && (
          <div className="space-y-2">
            <Label htmlFor="current">Current password</Label>
            <Input
              id="current"
              type={show ? "text" : "password"}
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />
          </div>
        )}
        <div className="space-y-2">
          <Label htmlFor="password">
            {hasPassword ? "New password" : "Password"}
          </Label>
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
        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : hasPassword ? (
            "Change password"
          ) : (
            "Create password"
          )}
        </Button>
      </form>
    </div>
  );
}

export default function AccountSecurityPage() {
  return (
    <ProtectedRoute>
      <SecurityForm />
    </ProtectedRoute>
  );
}
