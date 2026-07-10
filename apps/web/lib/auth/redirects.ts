import type { RoleName, User } from "@placementos/types";

import { ROLES } from "@/lib/auth/constants";

const ROLE_WORKSPACE_MAP: Record<RoleName, string> = {
  [ROLES.SUPER_ADMIN]: "/workspace/admin",
  [ROLES.PLACEMENT_CELL]: "/workspace/placement-cell",
  [ROLES.PLACEMENT_CONVENER]: "/workspace/convener",
  [ROLES.STUDENT]: "/workspace/student",
};

const ROLE_PRIORITY: RoleName[] = [
  ROLES.SUPER_ADMIN,
  ROLES.PLACEMENT_CELL,
  ROLES.PLACEMENT_CONVENER,
  ROLES.STUDENT,
];

export function getWorkspacePathForUser(user: User): string {
  const userRoles = new Set(user.roles.map((role) => role.name));

  for (const role of ROLE_PRIORITY) {
    if (userRoles.has(role)) {
      return ROLE_WORKSPACE_MAP[role];
    }
  }

  return ROLE_WORKSPACE_MAP[ROLES.STUDENT];
}

export const WORKSPACE_ROUTES = Object.values(ROLE_WORKSPACE_MAP);
