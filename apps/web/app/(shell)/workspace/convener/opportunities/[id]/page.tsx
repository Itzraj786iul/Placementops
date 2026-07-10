import { ProtectedRoute } from "@/components/auth/protected-route";
import { OpportunityOperationsWorkspace } from "@/features/convener-opportunities/components/opportunity-operations-workspace";
import { ROLES } from "@/lib/auth/constants";

const ALLOWED_ROLES = [
  ROLES.PLACEMENT_CONVENER,
  ROLES.PLACEMENT_CELL,
  ROLES.SUPER_ADMIN,
] as const;

type ConvenerOpportunityPageProps = {
  params: Promise<{ id: string }>;
};

export default async function ConvenerOpportunityPage({
  params,
}: ConvenerOpportunityPageProps) {
  const { id } = await params;

  return (
    <ProtectedRoute roles={[...ALLOWED_ROLES]}>
      <OpportunityOperationsWorkspace opportunityId={id} />
    </ProtectedRoute>
  );
}
