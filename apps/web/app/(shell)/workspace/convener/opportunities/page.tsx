import { ProtectedRoute } from "@/components/auth/protected-route";
import { ConvenerOpportunitiesIndex } from "@/features/convener-opportunities/components/convener-opportunities-index";
import { ROLES } from "@/lib/auth/constants";

const ALLOWED_ROLES = [
  ROLES.PLACEMENT_CONVENER,
  ROLES.PLACEMENT_CELL,
  ROLES.SUPER_ADMIN,
] as const;

export default function ConvenerOpportunitiesPage() {
  return (
    <ProtectedRoute roles={[...ALLOWED_ROLES]}>
      <ConvenerOpportunitiesIndex />
    </ProtectedRoute>
  );
}
