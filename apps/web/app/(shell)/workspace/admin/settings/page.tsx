import { ProtectedRoute } from "@/components/auth/protected-route";
import { SettingsWorkspace } from "@/features/admin-settings/components/settings-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function AdminSettingsPage() {
  return (
    <ProtectedRoute roles={[ROLES.SUPER_ADMIN]}>
      <SettingsWorkspace />
    </ProtectedRoute>
  );
}
