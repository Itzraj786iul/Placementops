import { Badge } from "@/components/ui/badge";
import { OWNERSHIP_LABELS } from "@/features/company-crm/constants";
import type { OwnershipType } from "@/features/company-crm/types";
import { cn } from "@/lib/utils";

type HandlerBadgeProps = {
  handlerId: string;
  ownershipType?: OwnershipType;
  branch?: string | null;
  className?: string;
};

export function HandlerBadge({
  handlerId,
  ownershipType,
  branch,
  className,
}: HandlerBadgeProps) {
  const shortId = handlerId.slice(0, 8);
  const label = branch ? `${shortId} · ${branch}` : shortId;

  return (
    <div className={cn("flex flex-wrap items-center gap-1.5", className)}>
      <Badge variant="secondary" className="font-normal">
        {label}
      </Badge>
      {ownershipType && (
        <Badge variant="outline" className="font-normal">
          {OWNERSHIP_LABELS[ownershipType]}
        </Badge>
      )}
    </div>
  );
}
