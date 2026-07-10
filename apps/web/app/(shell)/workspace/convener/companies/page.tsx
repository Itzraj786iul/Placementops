import { ProtectedRoute } from "@/components/auth/protected-route";
import { CompanyCrmWorkspace } from "@/features/company-crm/components/company-crm-workspace";
import { ROLES } from "@/lib/auth/constants";

const ALLOWED_ROLES = [
  ROLES.PLACEMENT_CONVENER,
  ROLES.PLACEMENT_CELL,
  ROLES.SUPER_ADMIN,
] as const;

export default function ConvenerCompaniesPage() {
  return (
    <ProtectedRoute roles={[...ALLOWED_ROLES]}>
      <CompanyCrmWorkspace />
    </ProtectedRoute>
  );
}
