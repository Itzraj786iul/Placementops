import type { ExportRequest } from "@/features/convener-opportunities/export/types";
import { ApiError } from "@/lib/api-client";

function parseFilename(contentDisposition: string | null): string | null {
  if (!contentDisposition) return null;
  const match = /filename="?([^"]+)"?/i.exec(contentDisposition);
  return match?.[1] ?? null;
}

export async function downloadOpportunityExport(
  opportunityId: string,
  payload: ExportRequest,
): Promise<void> {
  const response = await fetch(
    `/api/v1/opportunities/${opportunityId}/exports`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    let message = "Export failed. Please try again.";
    try {
      const data = (await response.json()) as { message?: string };
      if (data.message) message = data.message;
    } catch {
      // ignore parse errors
    }
    throw new ApiError(message, response.status);
  }

  const blob = await response.blob();
  const filename =
    parseFilename(response.headers.get("Content-Disposition")) ??
    `opportunity-${opportunityId}-applications.${payload.format}`;

  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}
