import { ProtectedRoute } from "@/components/auth/protected-route";
import { SeasonsWorkspace } from "@/features/admin-org/components/seasons-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminSeasonsPage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN, ROLES.PLACEMENT_CELL]}>
      <SeasonsWorkspace />
    </ProtectedRoute>
  );
}
