import Link from "next/link";

import { ProtectedRoute, RoleGuard } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { ROLES } from "@/lib/auth/constants";
import { WORKSPACE_CONFIG } from "@/lib/auth/workspaces";

const CARDS = [
  {
    title: "User & Role Management",
    description:
      "Search, filter, assign roles, and manage account status for PlacementOS users.",
    href: "/workspace/admin/users",
    cta: "Open users",
    superAdminOnly: false,
  },
  {
    title: "Departments",
    description:
      "Create, archive, and restore academic departments used across student profiles.",
    href: "/workspace/admin/departments",
    cta: "Open departments",
    superAdminOnly: false,
  },
  {
    title: "Placement Seasons",
    description:
      "Plan and activate placement years so opportunities and applications stay isolated.",
    href: "/workspace/admin/seasons",
    cta: "Open seasons",
    superAdminOnly: false,
  },
  {
    title: "System Settings",
    description:
      "Configure college identity, auth behaviour, notifications, and placement defaults.",
    href: "/workspace/admin/settings",
    cta: "Open settings",
    superAdminOnly: true,
  },
  {
    title: "System Health",
    description:
      "Live operational status for database, storage, email, auth, and platform stats.",
    href: "/workspace/admin/system-health",
    cta: "Open health",
    superAdminOnly: true,
  },
  {
    title: "Feature Flags",
    description:
      "Enable, disable, and roll out PlacementOS capabilities without code changes.",
    href: "/workspace/admin/feature-flags",
    cta: "Open flags",
    superAdminOnly: true,
  },
  {
    title: "Maintenance Mode",
    description:
      "Take PlacementOS offline for deployments and emergency fixes with a public banner.",
    href: "/workspace/admin/maintenance",
    cta: "Open maintenance",
    superAdminOnly: true,
  },
] as const;

export default function AdminWorkspacePage() {
  const config = WORKSPACE_CONFIG.admin;

  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN, ROLES.PLACEMENT_CELL]}>
      <div className="mx-auto max-w-3xl space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight">
            {config.title}
          </h1>
          <p className="text-muted-foreground mt-1 text-sm">
            {config.description}
          </p>
        </div>
        <div className="grid gap-4">
          {CARDS.map((card) => {
            const body = (
              <div className="rounded-lg border p-6">
                <h2 className="font-medium">{card.title}</h2>
                <p className="text-muted-foreground mt-1 text-sm">
                  {card.description}
                </p>
                <Button asChild className="mt-4">
                  <Link href={card.href}>{card.cta}</Link>
                </Button>
              </div>
            );
            if (card.superAdminOnly) {
              return (
                <RoleGuard key={card.href} role={ROLES.SUPER_ADMIN}>
                  {body}
                </RoleGuard>
              );
            }
            return <div key={card.href}>{body}</div>;
          })}
        </div>
      </div>
    </ProtectedRoute>
  );
}
