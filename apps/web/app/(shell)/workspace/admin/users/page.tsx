import { ProtectedRoute } from "@/components/auth/protected-route";
import { AdminUsersWorkspace } from "@/features/admin-users/components/admin-users-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminUsersPage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN, ROLES.PLACEMENT_CELL]}>
      <AdminUsersWorkspace />
    </ProtectedRoute>
  );
}
