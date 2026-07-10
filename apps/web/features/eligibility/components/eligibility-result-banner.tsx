import { cn } from "@/lib/utils";

type EligibilityResultBannerProps = {
  eligible: boolean;
  eligibleLabel?: string;
  ineligibleLabel?: string;
  className?: string;
};

export function EligibilityResultBanner({
  eligible,
  eligibleLabel = "Eligible",
  ineligibleLabel = "Not Eligible",
  className,
}: EligibilityResultBannerProps) {
  return (
    <div
      role="status"
      className={cn(
        "rounded-lg border px-4 py-3 text-sm font-medium",
        eligible
          ? "border-emerald-500/30 bg-emerald-500/10 text-emerald-800 dark:text-emerald-200"
          : "border-red-500/30 bg-red-500/10 text-red-800 dark:text-red-200",
        className,
      )}
    >
      {eligible ? eligibleLabel : ineligibleLabel}
    </div>
  );
}
