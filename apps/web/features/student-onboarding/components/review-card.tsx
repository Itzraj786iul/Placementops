import { Badge } from "@/components/ui/badge";
import type { VerificationStatus } from "@/features/student-onboarding/types";
import { cn } from "@/lib/utils";

type ReviewCardProps = {
  title: string;
  complete: boolean;
  /** Placement Cell verification for this section, when applicable. */
  verificationStatus?: VerificationStatus | null;
  children?: React.ReactNode;
  onEdit?: () => void;
  className?: string;
};

const VERIFICATION_LABEL: Record<VerificationStatus, string> = {
  PENDING: "Pending Placement Cell review",
  VERIFIED: "Verified",
  REJECTED: "Rejected",
};

export function ReviewCard({
  title,
  complete,
  verificationStatus,
  children,
  onEdit,
  className,
}: ReviewCardProps) {
  return (
    <div className={cn("rounded-lg border p-4", className)}>
      <div className="mb-3 flex items-start justify-between gap-3">
        <div className="space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <h4 className="font-medium">{title}</h4>
            <Badge
              variant="outline"
              className={cn(
                "border-transparent font-medium",
                complete
                  ? "bg-green-100 text-green-800 dark:bg-green-950 dark:text-green-300"
                  : "bg-muted text-muted-foreground",
              )}
            >
              {complete ? "Complete" : "Incomplete"}
            </Badge>
          </div>
          {verificationStatus && (
            <p className="text-muted-foreground text-xs">
              Verification: {VERIFICATION_LABEL[verificationStatus]}
            </p>
          )}
        </div>
        {onEdit && (
          <button
            type="button"
            onClick={onEdit}
            className="text-primary text-xs underline-offset-2 hover:underline"
          >
            Edit
          </button>
        )}
      </div>
      {children ?? (
        <p className="text-muted-foreground text-sm">
          {complete ? "Section complete" : "This section needs attention"}
        </p>
      )}
    </div>
  );
}
