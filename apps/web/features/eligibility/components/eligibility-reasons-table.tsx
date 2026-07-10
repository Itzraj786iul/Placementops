import { EligibilityEmptyState } from "@/features/eligibility/components/eligibility-empty-state";
import type { EligibilityReason } from "@/features/eligibility/types";

type EligibilityReasonsTableProps = {
  reasons: EligibilityReason[];
  emptyTitle?: string;
  emptyDescription?: string;
};

export function EligibilityReasonsTable({
  reasons,
  emptyTitle = "No failed rules",
  emptyDescription = "This student meets all configured eligibility criteria.",
}: EligibilityReasonsTableProps) {
  if (reasons.length === 0) {
    return (
      <EligibilityEmptyState
        title={emptyTitle}
        description={emptyDescription}
      />
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border">
      <table className="w-full min-w-[480px] text-left text-sm">
        <thead className="bg-muted/30 text-muted-foreground border-b text-xs">
          <tr>
            <th className="px-4 py-3 font-medium">Rule</th>
            <th className="px-4 py-3 font-medium">Expected</th>
            <th className="px-4 py-3 font-medium">Actual</th>
          </tr>
        </thead>
        <tbody>
          {reasons.map((reason) => (
            <tr
              key={`${reason.code}-${reason.expected}-${reason.actual}`}
              className="border-b last:border-0"
            >
              <td className="px-4 py-3">
                <p className="font-medium">{reason.title}</p>
                <p className="text-muted-foreground text-xs">{reason.code}</p>
              </td>
              <td className="text-muted-foreground px-4 py-3">
                {reason.expected}
              </td>
              <td className="px-4 py-3">{reason.actual}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
