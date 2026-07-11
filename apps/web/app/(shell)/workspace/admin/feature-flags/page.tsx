import { ProtectedRoute } from "@/components/auth/protected-route";
import { FeatureFlagsWorkspace } from "@/features/admin-feature-flags/components/feature-flags-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminFeatureFlagsPage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN]}>
      <FeatureFlagsWorkspace />
    </ProtectedRoute>
  );
}
