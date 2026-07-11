"use client";

import { Loader2 } from "lucide-react";
import * as React from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { inviteAdminUser } from "@/features/admin-users/api/admin-users-client";
import { ROLE_OPTIONS } from "@/features/admin-users/types";
import { ROLES } from "@/lib/auth/constants";
import { hasRole } from "@/lib/auth/roles";
import { useAuth } from "@/providers/auth-provider";

type InviteUserFormProps = {
  open: boolean;
  onClose: () => void;
  onInvited: () => void;
};

export function InviteUserForm({
  open,
  onClose,
  onInvited,
}: InviteUserFormProps) {
  const { user } = useAuth();
  const isSuperAdmin = hasRole(user, ROLES.SUPER_ADMIN);
  const [firstName, setFirstName] = React.useState("");
  const [lastName, setLastName] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [role, setRole] = React.useState("PLACEMENT_CONVENER");
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  if (!open) return null;

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setIsSubmitting(true);
    try {
      await inviteAdminUser({
        email: email.trim(),
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        role,
      });
      toast.success("Invitation sent — user will set a password via email");
      setFirstName("");
      setLastName("");
      setEmail("");
      setRole("PLACEMENT_CONVENER");
      onInvited();
      onClose();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : "Invite failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div className="bg-muted/30 border-b px-4 py-4">
      <form
        onSubmit={handleSubmit}
        className="mx-auto grid max-w-4xl gap-3 sm:grid-cols-2 lg:grid-cols-5"
      >
        <div className="space-y-1">
          <Label htmlFor="invite-first">First name</Label>
          <Input
            id="invite-first"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            required
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="invite-last">Last name</Label>
          <Input
            id="invite-last"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            required
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="invite-email">Email</Label>
          <Input
            id="invite-email"
            type="email"
            placeholder="name@nitrr.ac.in"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="invite-role">Role</Label>
          <Select
            id="invite-role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            {ROLE_OPTIONS.filter(
              (r) => r !== "SUPER_ADMIN" || isSuperAdmin,
            ).map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </Select>
        </div>
        <div className="flex items-end gap-2">
          <Button type="submit" disabled={isSubmitting} className="flex-1">
            {isSubmitting ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              "Send invite"
            )}
          </Button>
          <Button type="button" variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </div>
      </form>
    </div>
  );
}
