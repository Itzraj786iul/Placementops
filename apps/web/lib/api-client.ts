import { z } from "zod";

export const apiErrorSchema = z.object({
  message: z.string(),
  error_code: z.string().optional(),
  request_id: z.string().nullable().optional(),
});

export class ApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(response: Response): Promise<string> {
  try {
    const data = apiErrorSchema.parse(await response.json());
    return data.message;
  } catch {
    return "An unexpected error occurred. Please try again";
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`/api/v1${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    credentials: "same-origin",
  });

  if (!response.ok) {
    const message = await parseError(response);
    throw new ApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export function isOfflineError(error: unknown): boolean {
  return error instanceof TypeError && error.message === "Failed to fetch";
}
