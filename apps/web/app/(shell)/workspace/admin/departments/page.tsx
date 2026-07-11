import { ProtectedRoute } from "@/components/auth/protected-route";
import { DepartmentsWorkspace } from "@/features/admin-org/components/departments-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminDepartmentsPage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN, ROLES.PLACEMENT_CELL]}>
      <DepartmentsWorkspace />
    </ProtectedRoute>
  );
}
