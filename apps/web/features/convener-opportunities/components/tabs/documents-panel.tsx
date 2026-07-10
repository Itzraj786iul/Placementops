import { BACKEND_LIMITATIONS } from "@/features/convener-opportunities/constants";

const DOCUMENT_TYPES = [
  { label: "Job Description (JD)", type: "JD" },
  { label: "Eligibility PDF", type: "ELIGIBILITY" },
  { label: "Presentation (PPT)", type: "PPT" },
  { label: "Other documents", type: "OTHER" },
];

export function DocumentsPanel() {
  return (
    <div className="space-y-4 p-6">
      <p className="text-muted-foreground text-sm">
        {BACKEND_LIMITATIONS.noDocumentsList}
      </p>
      <div className="space-y-2">
        {DOCUMENT_TYPES.map((doc) => (
          <div
            key={doc.type}
            className="flex items-center justify-between rounded-lg border px-4 py-3 opacity-60"
          >
            <span className="text-sm">{doc.label}</span>
            <span className="text-muted-foreground text-xs">
              List endpoint unavailable
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
