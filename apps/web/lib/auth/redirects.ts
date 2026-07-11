import type { RoleName, User } from "@placementos/types";

import { ROLES } from "@/lib/auth/constants";

/** Highest priority first — must stay aligned with API `users/workspace.py`. */
export const ROLE_PRIORITY: RoleName[] = [
  ROLES.SUPER_ADMIN,
  ROLES.PLACEMENT_CELL,
  ROLES.PLACEMENT_CONVENER,
  ROLES.STUDENT,
];

export const ROLE_WORKSPACE_MAP: Record<RoleName, string> = {
  [ROLES.SUPER_ADMIN]: "/workspace/admin",
  [ROLES.PLACEMENT_CELL]: "/workspace/placement-cell",
  [ROLES.PLACEMENT_CONVENER]: "/workspace/convener",
  [ROLES.STUDENT]: "/workspace/student",
};

export const ROLE_DISPLAY_LABELS: Record<RoleName, string> = {
  [ROLES.SUPER_ADMIN]: "Super Admin",
  [ROLES.PLACEMENT_CELL]: "Placement Cell",
  [ROLES.PLACEMENT_CONVENER]: "Placement Convener",
  [ROLES.STUDENT]: "Student",
};

export const ACCOUNT_INACTIVE_PATH = "/account-inactive";
export const WELCOME_PATH = "/welcome";

export function getPrimaryRole(user: User): RoleName | null {
  if (user.primary_role) {
    return user.primary_role;
  }
  const userRoles = new Set(user.roles.map((role) => role.name));
  for (const role of ROLE_PRIORITY) {
    if (userRoles.has(role)) {
      return role;
    }
  }
  return null;
}

/**
 * Resolve post-auth destination from DB roles (via API fields when present).
 * Returns null when the user has no assignable workspace.
 */
export function getWorkspacePathForUser(user: User): string | null {
  if (user.workspace_path) {
    return user.workspace_path;
  }
  const role = getPrimaryRole(user);
  if (!role) {
    return null;
  }
  return ROLE_WORKSPACE_MAP[role];
}

export function getPostAuthPath(user: User, isNewUser = false): string {
  if (!user.is_active || user.roles.length === 0) {
    return ACCOUNT_INACTIVE_PATH;
  }
  if (isNewUser || user.needs_welcome) {
    return WELCOME_PATH;
  }
  return getWorkspacePathForUser(user) ?? ACCOUNT_INACTIVE_PATH;
}

export const WORKSPACE_ROUTES = Object.values(ROLE_WORKSPACE_MAP);
