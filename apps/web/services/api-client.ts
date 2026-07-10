import type { HealthCheckResponse } from "@placementos/types";

import { API_BASE_URL } from "@/lib/constants";

export async function fetchHealthCheck(): Promise<HealthCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    next: { revalidate: 60 },
  });

  if (!response.ok) {
    throw new Error("Health check failed");
  }

  return response.json() as Promise<HealthCheckResponse>;
}
