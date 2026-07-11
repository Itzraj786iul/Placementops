import type { RoleName } from "@placementos/types";

export const ROLES = {
  SUPER_ADMIN: "SUPER_ADMIN",
  PLACEMENT_CELL: "PLACEMENT_CELL",
  PLACEMENT_CONVENER: "PLACEMENT_CONVENER",
  STUDENT: "STUDENT",
} as const satisfies Record<string, RoleName>;

export const PUBLIC_ROUTES = [
  "/",
  "/login",
  "/signup",
  "/account-inactive",
] as const;

export const AUTH_ROUTES = ["/auth/callback"] as const;

export const COOKIE_NAMES = {
  ACCESS_TOKEN: "access_token",
  REFRESH_TOKEN: "refresh_token",
} as const;
