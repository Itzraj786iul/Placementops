export const NAV_ITEMS = [
  {
    title: "Student",
    href: "/workspace/student",
    icon: "GraduationCap",
    roles: ["STUDENT", "SUPER_ADMIN"],
  },
  {
    title: "Opportunities",
    href: "/workspace/student/opportunities",
    icon: "Briefcase",
    roles: ["STUDENT", "SUPER_ADMIN"],
  },
  {
    title: "Convener",
    href: "/workspace/convener",
    icon: "Users",
    roles: ["PLACEMENT_CONVENER", "SUPER_ADMIN"],
  },
  {
    title: "Companies",
    href: "/workspace/convener/companies",
    icon: "Building2",
    roles: ["PLACEMENT_CONVENER", "PLACEMENT_CELL", "SUPER_ADMIN"],
  },
  {
    title: "Opportunity Ops",
    href: "/workspace/convener/opportunities",
    icon: "Briefcase",
    roles: ["PLACEMENT_CONVENER", "PLACEMENT_CELL", "SUPER_ADMIN"],
  },
  {
    title: "Placement Cell",
    href: "/workspace/placement-cell",
    icon: "Building2",
    roles: ["PLACEMENT_CELL", "SUPER_ADMIN"],
  },
  {
    title: "Admin",
    href: "/workspace/admin",
    icon: "Shield",
    roles: ["SUPER_ADMIN"],
  },
] as const;
