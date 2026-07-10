import type {
  ApplicationFilters,
  ApplicationSortField,
  EnrichedApplication,
  SortDirection,
} from "@/features/convener-opportunities/types";
import type { ApplicationSnapshot } from "@/features/convener-opportunities/types";
import type { ApplicationListItem } from "@/features/student-opportunities/types";

export function getStudentName(snapshot?: ApplicationSnapshot): string {
  const personal = snapshot?.student_profile_snapshot.personal_information;
  if (!personal) return "Unknown";
  return `${personal.first_name} ${personal.last_name}`.trim();
}

export function enrichApplications(
  applications: ApplicationListItem[],
  snapshots: Map<string, ApplicationSnapshot>,
): EnrichedApplication[] {
  return applications.map((application) => ({
    application,
    snapshot: snapshots.get(application.id),
  }));
}

export function extractDepartments(items: EnrichedApplication[]): string[] {
  return [
    ...new Set(
      items
        .map((item) => item.snapshot?.student_profile_snapshot.department_name)
        .filter((name): name is string => Boolean(name)),
    ),
  ].sort();
}

export function extractBranches(items: EnrichedApplication[]): string[] {
  return [
    ...new Set(
      items
        .map((item) => item.snapshot?.student_profile_snapshot.department_code)
        .filter((code): code is string => Boolean(code)),
    ),
  ].sort();
}

function compareStrings(
  a: string,
  b: string,
  direction: SortDirection,
): number {
  const result = a.localeCompare(b, undefined, { sensitivity: "base" });
  return direction === "asc" ? result : -result;
}

function compareNumbers(
  a: number,
  b: number,
  direction: SortDirection,
): number {
  return direction === "asc" ? a - b : b - a;
}

export function filterApplications(
  items: EnrichedApplication[],
  filters: ApplicationFilters,
): EnrichedApplication[] {
  const search = filters.search.trim().toLowerCase();

  return items.filter(({ application, snapshot }) => {
    if (filters.status && application.status !== filters.status) return false;

    const profile = snapshot?.student_profile_snapshot;
    if (filters.department && profile?.department_name !== filters.department) {
      return false;
    }
    if (filters.branch && profile?.department_code !== filters.branch)
      return false;

    if (search) {
      const name = getStudentName(snapshot).toLowerCase();
      const roll = profile?.roll_number?.toLowerCase() ?? "";
      const dept = profile?.department_name?.toLowerCase() ?? "";
      const haystack = [name, roll, dept, application.status].join(" ");
      if (!haystack.includes(search)) return false;
    }

    return true;
  });
}

export function sortApplications(
  items: EnrichedApplication[],
  field: ApplicationSortField,
  direction: SortDirection,
): EnrichedApplication[] {
  const sorted = [...items];

  sorted.sort((a, b) => {
    const profileA = a.snapshot?.student_profile_snapshot;
    const profileB = b.snapshot?.student_profile_snapshot;

    switch (field) {
      case "name":
        return compareStrings(
          getStudentName(a.snapshot),
          getStudentName(b.snapshot),
          direction,
        );
      case "roll_number":
        return compareStrings(
          profileA?.roll_number ?? "",
          profileB?.roll_number ?? "",
          direction,
        );
      case "department":
        return compareStrings(
          profileA?.department_name ?? "",
          profileB?.department_name ?? "",
          direction,
        );
      case "cgpa": {
        const cgpaA = parseFloat(
          profileA?.academic_information?.current_cgpa ?? "0",
        );
        const cgpaB = parseFloat(
          profileB?.academic_information?.current_cgpa ?? "0",
        );
        return compareNumbers(cgpaA, cgpaB, direction);
      }
      case "applied_at":
        return compareStrings(
          a.application.applied_at,
          b.application.applied_at,
          direction,
        );
      case "status":
        return compareStrings(
          a.application.status,
          b.application.status,
          direction,
        );
      default:
        return 0;
    }
  });

  return sorted;
}

export function paginateApplications<T>(
  items: T[],
  page: number,
  pageSize: number,
): T[] {
  const start = (page - 1) * pageSize;
  return items.slice(start, start + pageSize);
}

export function countByStatus(
  items: EnrichedApplication[],
): Partial<Record<ApplicationListItem["status"], number>> {
  return items.reduce<Partial<Record<ApplicationListItem["status"], number>>>(
    (acc, item) => {
      acc[item.application.status] = (acc[item.application.status] ?? 0) + 1;
      return acc;
    },
    {},
  );
}
