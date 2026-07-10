import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

type SummaryCardProps = {
  label: string;
  value: ReactNode;
  hint?: string;
  className?: string;
};

export function SummaryCard({
  label,
  value,
  hint,
  className,
}: SummaryCardProps) {
  return (
    <div className={cn("bg-card rounded-lg border p-4 shadow-sm", className)}>
      <p className="text-muted-foreground text-xs font-medium tracking-wide uppercase">
        {label}
      </p>
      <p className="mt-2 text-2xl font-semibold">{value}</p>
      {hint && <p className="text-muted-foreground mt-1 text-xs">{hint}</p>}
    </div>
  );
}
