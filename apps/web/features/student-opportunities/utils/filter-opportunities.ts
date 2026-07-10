import type {
  ApplicationListItem,
  EnrichedOpportunity,
  OpportunityDetail,
  OpportunityFilters,
  OpportunityListItem,
} from "@/features/student-opportunities/types";

export function formatCtc(
  min: string | null | undefined,
  max: string | null | undefined,
): string {
  if (min == null && max == null) return "Not disclosed";
  if (min != null && max != null) return `₹${min} – ₹${max} LPA`;
  if (min != null) return `From ₹${min} LPA`;
  return `Up to ₹${max} LPA`;
}

export function parseCtcValue(value: string | null | undefined): number | null {
  if (value == null) return null;
  const parsed = parseFloat(value);
  return Number.isNaN(parsed) ? null : parsed;
}

export function isDeadlinePassed(deadline: string): boolean {
  return new Date(deadline).getTime() <= Date.now();
}

export function buildApplicationMap(
  applications: ApplicationListItem[],
): Map<string, ApplicationListItem> {
  return new Map(applications.map((app) => [app.hiring_opportunity_id, app]));
}

export function enrichOpportunities(
  list: OpportunityListItem[],
  details: Map<string, OpportunityDetail>,
  applications: Map<string, ApplicationListItem>,
): EnrichedOpportunity[] {
  return list.map((item) => ({
    list: item,
    detail: details.get(item.id),
    application: applications.get(item.id),
  }));
}

export function extractLocations(items: OpportunityListItem[]): string[] {
  return [...new Set(items.map((o) => o.location).filter(Boolean))].sort();
}

export function filterOpportunities(
  items: EnrichedOpportunity[],
  filters: OpportunityFilters,
): EnrichedOpportunity[] {
  const search = filters.search.trim().toLowerCase();

  return items.filter(({ list, detail, application }) => {
    if (search) {
      const haystack = [
        list.title,
        list.role,
        list.location,
        list.employment_type,
      ]
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(search)) return false;
    }

    if (
      filters.employmentType &&
      list.employment_type !== filters.employmentType
    ) {
      return false;
    }

    if (filters.location && list.location !== filters.location) return false;

    if (filters.mode && list.mode !== filters.mode) return false;

    if (filters.ctcMin != null || filters.ctcMax != null) {
      const min = parseCtcValue(detail?.ctc_min);
      const max = parseCtcValue(detail?.ctc_max);
      if (min == null && max == null) return false;
      if (filters.ctcMin != null && max != null && max < filters.ctcMin)
        return false;
      if (filters.ctcMax != null && min != null && min > filters.ctcMax)
        return false;
    }

    if (filters.applicationStatus) {
      if (filters.applicationStatus === "NOT_APPLIED") {
        if (application) return false;
      } else if (
        !application ||
        application.status !== filters.applicationStatus
      ) {
        return false;
      }
    }

    return true;
  });
}
