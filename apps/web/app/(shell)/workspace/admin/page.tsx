import Link from "next/link";

import { ProtectedRoute } from "@/components/auth/protected-route";
import { Button } from "@/components/ui/button";
import { ROLES } from "@/lib/auth/constants";
import { WORKSPACE_CONFIG } from "@/lib/auth/workspaces";

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
        <div className="rounded-lg border p-6">
          <h2 className="font-medium">User & Role Management</h2>
          <p className="text-muted-foreground mt-1 text-sm">
            Search, filter, assign roles, and manage account status for
            PlacementOS users.
          </p>
          <Button asChild className="mt-4">
            <Link href="/workspace/admin/users">Open users</Link>
          </Button>
        </div>
      </div>
    </ProtectedRoute>
  );
}
