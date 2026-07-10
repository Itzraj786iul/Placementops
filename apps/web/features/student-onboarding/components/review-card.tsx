import { StatusBadge } from "@/features/student-onboarding/components/status-badge";
import { cn } from "@/lib/utils";

type ReviewCardProps = {
  title: string;
  complete: boolean;
  children?: React.ReactNode;
  onEdit?: () => void;
  className?: string;
};

export function ReviewCard({
  title,
  complete,
  children,
  onEdit,
  className,
}: ReviewCardProps) {
  return (
    <div className={cn("rounded-lg border p-4", className)}>
      <div className="mb-3 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <h4 className="font-medium">{title}</h4>
          <StatusBadge status={complete ? "VERIFIED" : "PENDING"} />
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
