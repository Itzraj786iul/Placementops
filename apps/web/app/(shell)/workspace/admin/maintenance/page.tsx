import { ProtectedRoute } from "@/components/auth/protected-route";
import { MaintenanceWorkspace } from "@/features/admin-maintenance/components/maintenance-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminMaintenancePage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN]}>
      <MaintenanceWorkspace />
    </ProtectedRoute>
  );
}
