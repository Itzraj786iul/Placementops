import { ProtectedRoute } from "@/components/auth/protected-route";
import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { ROLES } from "@/lib/auth/constants";
import { WORKSPACE_CONFIG } from "@/lib/auth/workspaces";

export default function PlacementCellWorkspacePage() {
  const config = WORKSPACE_CONFIG["placement-cell"];

  return (
    <ProtectedRoute roles={[ROLES.PLACEMENT_CELL, ROLES.SUPER_ADMIN]}>
      <WorkspaceShell title={config.title} description={config.description} />
    </ProtectedRoute>
  );
}
