import { BACKEND_LIMITATIONS } from "@/features/student-opportunities/constants";

export function DocumentsTab() {
  return (
    <div className="space-y-4 p-4">
      <p className="text-muted-foreground text-sm">
        {BACKEND_LIMITATIONS.noDocumentsList}
      </p>
      <div className="space-y-2">
        {["Job Description (JD)", "Eligibility PDF", "Presentation (PPT)"].map(
          (label) => (
            <div
              key={label}
              className="flex items-center justify-between rounded-lg border px-4 py-3 opacity-60"
            >
              <span className="text-sm">{label}</span>
              <span className="text-muted-foreground text-xs">Unavailable</span>
            </div>
          ),
        )}
      </div>
    </div>
  );
}
