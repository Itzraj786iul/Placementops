"use client";

import { toast } from "sonner";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { SlideOver } from "@/features/company-crm/components/slide-over";
import {
  useAdminUser,
  useAdminUserAudit,
  useAdminUserMutations,
} from "@/features/admin-users/hooks/use-admin-users";
import { ROLE_OPTIONS, STATUS_OPTIONS } from "@/features/admin-users/types";
import { ROLES } from "@/lib/auth/constants";
import { hasRole } from "@/lib/auth/roles";
import { useAuth } from "@/providers/auth-provider";

type UserDetailDrawerProps = {
  userId: string | null;
  onClose: () => void;
};

export function UserDetailDrawer({ userId, onClose }: UserDetailDrawerProps) {
  const { user: actor } = useAuth();
  const detail = useAdminUser(userId);
  const audit = useAdminUserAudit(userId);
  const { updateUser, updateRoles } = useAdminUserMutations();
  const isSuperAdmin = hasRole(actor, ROLES.SUPER_ADMIN);

  const data = detail.data;

  return (
    <SlideOver
      open={Boolean(userId)}
      onClose={onClose}
      title={data?.display_name ?? "User details"}
      description={data?.college_email}
    >
      {detail.isLoading && (
        <div className="space-y-3">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="bg-muted h-10 animate-pulse rounded" />
          ))}
        </div>
      )}

      {detail.isError && (
        <p className="text-destructive text-sm">Failed to load user.</p>
      )}

      {data && (
        <div className="space-y-6">
          <section className="flex items-center gap-3">
            <Avatar className="h-12 w-12">
              {data.profile_picture && (
                <AvatarImage
                  src={data.profile_picture}
                  alt={data.display_name}
                />
              )}
              <AvatarFallback>
                {data.first_name[0]}
                {data.last_name[0]}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="font-medium">{data.display_name}</p>
              <p className="text-muted-foreground text-xs capitalize">
                {data.status}
                {data.email_verified ? " · verified email" : ""}
              </p>
            </div>
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Profile</h3>
            <dl className="grid grid-cols-2 gap-2 text-xs">
              <div>
                <dt className="text-muted-foreground">Department</dt>
                <dd>{data.department_name ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Roll</dt>
                <dd>{data.roll_number ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Registration</dt>
                <dd>{data.registration_number ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Graduation</dt>
                <dd>{data.graduation_year ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Verification</dt>
                <dd>{data.verification_status ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-muted-foreground">Profile status</dt>
                <dd>{data.profile_status ?? "—"}</dd>
              </div>
            </dl>
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Account status</h3>
            <Select
              value={data.status}
              disabled={updateUser.isPending}
              onChange={async (e) => {
                try {
                  await updateUser.mutateAsync({
                    id: data.id,
                    payload: { status: e.target.value },
                  });
                  toast.success("Status updated");
                } catch (err) {
                  toast.error(
                    err instanceof Error ? err.message : "Update failed",
                  );
                }
              }}
            >
              {STATUS_OPTIONS.filter(
                (s) => s !== "archived" || isSuperAdmin,
              ).map((status) => (
                <option key={status} value={status}>
                  {status}
                </option>
              ))}
            </Select>
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Roles</h3>
            <ul className="space-y-2">
              {data.role_assignments.map((role) => (
                <li
                  key={role.role_id}
                  className="flex items-center justify-between rounded border px-3 py-2 text-sm"
                >
                  <span>
                    {role.role_name}
                    {role.is_primary ? " (primary)" : ""}
                  </span>
                  <Button
                    type="button"
                    size="sm"
                    variant="outline"
                    disabled={
                      updateRoles.isPending ||
                      (role.role_name === "SUPER_ADMIN" && !isSuperAdmin)
                    }
                    onClick={async () => {
                      try {
                        await updateRoles.mutateAsync({
                          id: data.id,
                          payload: { remove: [role.role_name] },
                        });
                        toast.success("Role removed");
                      } catch (err) {
                        toast.error(
                          err instanceof Error ? err.message : "Failed",
                        );
                      }
                    }}
                  >
                    Remove
                  </Button>
                </li>
              ))}
            </ul>
            <div className="flex gap-2">
              <Select
                defaultValue=""
                disabled={updateRoles.isPending}
                onChange={async (e) => {
                  const role = e.target.value;
                  if (!role) return;
                  try {
                    await updateRoles.mutateAsync({
                      id: data.id,
                      payload: { assign: [role] },
                    });
                    toast.success("Role assigned");
                    e.target.value = "";
                  } catch (err) {
                    toast.error(err instanceof Error ? err.message : "Failed");
                  }
                }}
              >
                <option value="">Assign role…</option>
                {ROLE_OPTIONS.filter(
                  (r) =>
                    (r !== "SUPER_ADMIN" || isSuperAdmin) &&
                    !data.roles.some((x) => x.name === r),
                ).map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </Select>
              <Select
                value={data.primary_role ?? ""}
                disabled={updateRoles.isPending || data.roles.length === 0}
                onChange={async (e) => {
                  try {
                    await updateRoles.mutateAsync({
                      id: data.id,
                      payload: { primary_role: e.target.value || null },
                    });
                    toast.success("Primary role updated");
                  } catch (err) {
                    toast.error(err instanceof Error ? err.message : "Failed");
                  }
                }}
              >
                <option value="">Primary role…</option>
                {data.roles.map((role) => (
                  <option key={role.id} value={role.name}>
                    {role.name}
                  </option>
                ))}
              </Select>
            </div>
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Statistics</h3>
            <dl className="grid grid-cols-2 gap-2 text-xs">
              {Object.entries(data.statistics).map(([key, value]) => (
                <div key={key}>
                  <dt className="text-muted-foreground capitalize">{key}</dt>
                  <dd>{value ?? "—"}</dd>
                </div>
              ))}
            </dl>
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Role history</h3>
            {data.role_history.length === 0 ? (
              <p className="text-muted-foreground text-xs">
                No role changes yet.
              </p>
            ) : (
              <ul className="space-y-2 text-xs">
                {data.role_history.map((h) => (
                  <li key={h.id} className="rounded border px-3 py-2">
                    <p className="font-medium">
                      {h.action} {h.role_name}
                    </p>
                    <p className="text-muted-foreground">
                      {new Date(h.created_at).toLocaleString()}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Audit timeline</h3>
            {audit.isLoading && (
              <div className="bg-muted h-16 animate-pulse rounded" />
            )}
            {(audit.data?.items.length ?? 0) === 0 && !audit.isLoading && (
              <p className="text-muted-foreground text-xs">No audit events.</p>
            )}
            <ul className="space-y-2 text-xs">
              {audit.data?.items.map((item) => (
                <li key={item.id} className="rounded border px-3 py-2">
                  <p className="font-medium">
                    {item.action} · {item.entity_type}
                  </p>
                  <p className="text-muted-foreground">
                    {new Date(item.performed_at).toLocaleString()}
                  </p>
                </li>
              ))}
            </ul>
          </section>

          <section className="space-y-2">
            <h3 className="text-sm font-semibold">Current sessions</h3>
            <p className="text-muted-foreground text-xs">
              Session listing is not available yet (placeholder).
            </p>
          </section>
        </div>
      )}
    </SlideOver>
  );
}
