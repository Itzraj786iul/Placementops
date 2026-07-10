import type {
  CompanyFilters,
  CompanyListItem,
} from "@/features/company-crm/types";

export function filterCompanies(
  companies: CompanyListItem[],
  filters: CompanyFilters,
): CompanyListItem[] {
  const search = filters.search.trim().toLowerCase();

  return companies.filter((company) => {
    if (search) {
      const haystack = [company.name, company.industry, company.company_type]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      if (!haystack.includes(search)) return false;
    }

    if (filters.status && company.status !== filters.status) return false;

    if (filters.industry && company.industry !== filters.industry) return false;

    if (
      filters.pipelineStage &&
      company.pipeline?.current_stage !== filters.pipelineStage
    ) {
      return false;
    }

    if (filters.handlerId) {
      if (company.active_handler?.handler_user_id !== filters.handlerId) {
        return false;
      }
    }

    if (filters.ownershipType) {
      if (company.active_handler?.ownership_type !== filters.ownershipType) {
        return false;
      }
    }

    return true;
  });
}

export function extractIndustries(companies: CompanyListItem[]): string[] {
  const set = new Set<string>();
  for (const company of companies) {
    if (company.industry) set.add(company.industry);
  }
  return Array.from(set).sort();
}

export function extractHandlers(
  companies: CompanyListItem[],
): { id: string; label: string }[] {
  const map = new Map<string, string>();
  for (const company of companies) {
    const handler = company.active_handler;
    if (handler) {
      map.set(handler.handler_user_id, handler.handler_user_id.slice(0, 8));
    }
  }
  return Array.from(map.entries()).map(([id, label]) => ({ id, label }));
}

export function formatRelativeDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}
