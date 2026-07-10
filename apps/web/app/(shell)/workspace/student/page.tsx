import { ProtectedRoute } from "@/components/auth/protected-route";
import { OnboardingWizard } from "@/features/student-onboarding/components/onboarding-wizard";
import { ROLES } from "@/lib/auth/constants";

export default function StudentWorkspacePage() {
  return (
    <ProtectedRoute roles={[ROLES.STUDENT, ROLES.SUPER_ADMIN]}>
      <OnboardingWizard />
    </ProtectedRoute>
  );
}
