import { ProtectedRoute } from "@/components/auth/protected-route";
import { SystemHealthWorkspace } from "@/features/admin-health/components/system-health-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminSystemHealthPage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN]}>
      <SystemHealthWorkspace />
    </ProtectedRoute>
  );
}
