import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { SectionStatusBadge } from "@/features/student-onboarding/components/completion-assistant";
import { cn } from "@/lib/utils";

type SectionCardProps = {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  status?: "complete" | "incomplete" | "not_started";
  focusId?: string;
};

export function SectionCard({
  title,
  description,
  children,
  className,
  status,
  focusId,
}: SectionCardProps) {
  return (
    <Card
      className={cn("border-border/60 shadow-none", className)}
      data-completion-focus={focusId}
    >
      <CardHeader className="pb-4">
        <div className="flex flex-wrap items-center gap-2">
          <CardTitle className="text-lg">{title}</CardTitle>
          {status && <SectionStatusBadge status={status} />}
        </div>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>{children}</CardContent>
    </Card>
  );
}
