import type {
  ImportConfirmResponse,
  ImportPreviewResponse,
  ImportableStatus,
  MatchField,
} from "@/features/convener-opportunities/import/types";
import { ApiError } from "@/lib/api-client";

async function parseApiError(
  response: Response,
  fallback: string,
): Promise<string> {
  try {
    const data = (await response.json()) as { message?: string };
    if (data.message) return data.message;
  } catch {
    // ignore
  }
  return fallback;
}

export async function previewShortlistImport(
  opportunityId: string,
  file: File,
  matchField: MatchField,
  targetStatus: ImportableStatus,
): Promise<ImportPreviewResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("match_field", matchField);
  form.append("target_status", targetStatus);

  const response = await fetch(
    `/api/v1/opportunities/${opportunityId}/shortlist-imports/preview`,
    {
      method: "POST",
      credentials: "same-origin",
      body: form,
    },
  );

  if (!response.ok) {
    throw new ApiError(
      await parseApiError(response, "Import preview failed."),
      response.status,
    );
  }

  return response.json() as Promise<ImportPreviewResponse>;
}

export async function confirmShortlistImport(
  opportunityId: string,
  importId: string,
): Promise<ImportConfirmResponse> {
  const response = await fetch(
    `/api/v1/opportunities/${opportunityId}/shortlist-imports/${importId}/confirm`,
    {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    },
  );

  if (!response.ok) {
    throw new ApiError(
      await parseApiError(response, "Import confirm failed."),
      response.status,
    );
  }

  return response.json() as Promise<ImportConfirmResponse>;
}
