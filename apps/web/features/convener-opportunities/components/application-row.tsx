import { StatusBadge } from "@/features/student-opportunities/components/status-badge";
import type { EnrichedApplication } from "@/features/convener-opportunities/types";
import { getStudentName } from "@/features/convener-opportunities/utils/application-utils";
import { cn } from "@/lib/utils";

type ApplicationRowProps = {
  item: EnrichedApplication;
  onSelect: (applicationId: string) => void;
};

export function ApplicationRow({ item, onSelect }: ApplicationRowProps) {
  const { application, snapshot } = item;
  const profile = snapshot?.student_profile_snapshot;
  const loadingSnapshot = !snapshot;

  return (
    <tr
      className={cn(
        "hover:bg-muted/50 cursor-pointer border-b transition-colors",
        "focus-within:bg-muted/50",
      )}
      onClick={() => onSelect(application.id)}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          onSelect(application.id);
        }
      }}
      tabIndex={0}
      aria-label={`View application for ${getStudentName(snapshot)}`}
    >
      <td className="px-4 py-3 text-sm">
        {loadingSnapshot ? (
          <span className="text-muted-foreground">Loading...</span>
        ) : (
          getStudentName(snapshot)
        )}
      </td>
      <td className="px-4 py-3 text-sm">{profile?.roll_number ?? "—"}</td>
      <td className="px-4 py-3 text-sm">{profile?.department_name ?? "—"}</td>
      <td className="px-4 py-3 text-sm">
        {profile?.academic_information?.current_cgpa ?? "—"}
      </td>
      <td className="px-4 py-3 text-sm">
        {snapshot?.resume_snapshot.name ?? "—"}
      </td>
      <td className="px-4 py-3 text-sm">
        {new Date(application.applied_at).toLocaleString(undefined, {
          dateStyle: "medium",
          timeStyle: "short",
        })}
      </td>
      <td className="px-4 py-3">
        <StatusBadge status={application.status} />
      </td>
    </tr>
  );
}
