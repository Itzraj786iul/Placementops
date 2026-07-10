import type {
  AuthTokens,
  MessageResponse,
  Role,
  User,
} from "@placementos/types";

import {
  apiErrorSchema,
  authTokensSchema,
  messageResponseSchema,
  userSchema,
} from "@/lib/auth/schemas";

const API_PREFIX = "/api/v1";

class AuthApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
  ) {
    super(message);
    this.name = "AuthApiError";
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

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_PREFIX}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    credentials: "same-origin",
  });

  if (!response.ok) {
    const message = await parseError(response);
    throw new AuthApiError(message, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function fetchCurrentUser(): Promise<User> {
  const data = await request<unknown>("/auth/me");
  return userSchema.parse(data);
}

export async function exchangeAuthCode(code: string): Promise<AuthTokens> {
  const data = await request<unknown>("/auth/exchange", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
  return authTokensSchema.parse(data);
}

export async function devLogin(
  email: string,
  password: string,
): Promise<AuthTokens> {
  const data = await request<unknown>("/auth/dev/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  return authTokensSchema.parse(data);
}

export async function logout(): Promise<MessageResponse> {
  const data = await request<unknown>("/auth/logout", {
    method: "POST",
  });
  return messageResponseSchema.parse(data);
}

export async function fetchRoles(): Promise<Role[]> {
  return request<Role[]>("/roles");
}

export function getGoogleLoginUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return `${apiUrl}/api/v1/auth/google/login`;
}

export { AuthApiError };
