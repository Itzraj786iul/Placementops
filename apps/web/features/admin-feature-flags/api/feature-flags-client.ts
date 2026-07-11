import { apiRequest } from "@/lib/api-client";

export type FeatureFlag = {
  id: string | null;
  key: string;
  name: string;
  description: string | null;
  enabled: boolean;
  scope: string;
  metadata: Record<string, unknown> | null;
  updated_by: string | null;
  updated_by_email: string | null;
  updated_at: string | null;
  critical: boolean;
  persisted: boolean;
};

export type FeatureFlagListResponse = {
  items: FeatureFlag[];
  total: number;
  critical_keys: string[];
};

export async function fetchFeatureFlags(params?: {
  search?: string;
}): Promise<FeatureFlagListResponse> {
  const q = new URLSearchParams();
  if (params?.search) q.set("search", params.search);
  const suffix = q.toString() ? `?${q}` : "";
  return apiRequest(`/admin/feature-flags${suffix}`);
}

export async function patchFeatureFlag(
  key: string,
  payload: {
    enabled?: boolean;
    name?: string;
    description?: string | null;
    scope?: string;
    metadata?: Record<string, unknown>;
    confirm: boolean;
  },
): Promise<FeatureFlag> {
  return apiRequest(`/admin/feature-flags/${encodeURIComponent(key)}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
