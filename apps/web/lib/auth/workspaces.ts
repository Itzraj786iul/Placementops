import type { RoleName } from "@placementos/types";

import { ROLES } from "@/lib/auth/constants";

type WorkspaceConfig = {
  title: string;
  description: string;
  role: RoleName;
};

export const WORKSPACE_CONFIG: Record<string, WorkspaceConfig> = {
  student: {
    title: "Student Workspace",
    description: "Your placement portal for applications and opportunities.",
    role: ROLES.STUDENT,
  },
  convener: {
    title: "Convener Workspace",
    description: "Manage placement activities and coordinate drives.",
    role: ROLES.PLACEMENT_CONVENER,
  },
  "placement-cell": {
    title: "Placement Cell Workspace",
    description: "Oversee recruitment operations and company relations.",
    role: ROLES.PLACEMENT_CELL,
  },
  admin: {
    title: "Admin Workspace",
    description: "System administration and configuration.",
    role: ROLES.SUPER_ADMIN,
  },
};
