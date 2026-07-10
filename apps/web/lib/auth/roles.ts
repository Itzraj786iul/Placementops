import type { RoleName, User } from "@placementos/types";

export function hasRole(
  user: User | null | undefined,
  role: RoleName,
): boolean {
  if (!user) return false;
  return user.roles.some((userRole) => userRole.name === role);
}

export function hasAnyRole(
  user: User | null | undefined,
  roles: RoleName[],
): boolean {
  if (!user) return false;
  const userRoles = new Set(user.roles.map((role) => role.name));
  return roles.some((role) => userRoles.has(role));
}

export function requireRole(
  user: User | null | undefined,
  role: RoleName,
): void {
  if (!hasRole(user, role)) {
    throw new Error(`Access denied: ${role} role required`);
  }
}

export function getUserDisplayName(user: User): string {
  return `${user.first_name} ${user.last_name}`.trim();
}

export function getUserInitials(user: User): string {
  const first = user.first_name.charAt(0).toUpperCase();
  const last = user.last_name.charAt(0).toUpperCase();
  return `${first}${last}` || "U";
}
