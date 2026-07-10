import { ProtectedRoute } from "@/components/auth/protected-route";
import { WorkspaceShell } from "@/components/workspace/workspace-shell";
import { ROLES } from "@/lib/auth/constants";
import { WORKSPACE_CONFIG } from "@/lib/auth/workspaces";

export default function ConvenerWorkspacePage() {
  const config = WORKSPACE_CONFIG.convener;

  return (
    <ProtectedRoute roles={[ROLES.PLACEMENT_CONVENER, ROLES.SUPER_ADMIN]}>
      <WorkspaceShell title={config.title} description={config.description} />
    </ProtectedRoute>
  );
}
