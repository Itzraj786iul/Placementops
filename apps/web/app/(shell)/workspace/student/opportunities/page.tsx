import { ProtectedRoute } from "@/components/auth/protected-route";
import { StudentOpportunityWorkspace } from "@/features/student-opportunities/components/student-opportunity-workspace";
import { ROLES } from "@/lib/auth/constants";

export default function StudentOpportunitiesPage() {
  return (
    <ProtectedRoute roles={[ROLES.STUDENT, ROLES.SUPER_ADMIN]}>
      <StudentOpportunityWorkspace />
    </ProtectedRoute>
  );
}
