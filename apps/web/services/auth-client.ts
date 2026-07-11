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

export async function passwordLogin(payload: {
  email: string;
  password: string;
  remember_me?: boolean;
}): Promise<AuthTokens> {
  const data = await request<unknown>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return authTokensSchema.parse(data);
}

export async function registerAccount(payload: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}): Promise<MessageResponse> {
  const data = await request<unknown>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return messageResponseSchema.parse(data);
}

export async function forgotPassword(email: string): Promise<MessageResponse> {
  const data = await request<unknown>("/auth/password/forgot", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
  return messageResponseSchema.parse(data);
}

export async function resetPassword(
  token: string,
  password: string,
): Promise<MessageResponse> {
  const data = await request<unknown>("/auth/password/reset", {
    method: "POST",
    body: JSON.stringify({ token, password }),
  });
  return messageResponseSchema.parse(data);
}

export async function verifyEmail(token: string): Promise<MessageResponse> {
  const data = await request<unknown>("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
  return messageResponseSchema.parse(data);
}

export async function activateAccount(payload: {
  token: string;
  password: string;
  confirm_password: string;
}): Promise<AuthTokens> {
  const data = await request<unknown>("/auth/activate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return authTokensSchema.parse(data);
}

export async function createPassword(
  password: string,
  confirmPassword: string,
): Promise<User> {
  const data = await request<unknown>("/auth/password", {
    method: "POST",
    body: JSON.stringify({
      password,
      confirm_password: confirmPassword,
    }),
  });
  return userSchema.parse(data);
}

export async function changePassword(payload: {
  current_password: string;
  new_password: string;
  confirm_password: string;
}): Promise<MessageResponse> {
  const data = await request<unknown>("/auth/password/change", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  return messageResponseSchema.parse(data);
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

export async function completeWelcome(): Promise<User> {
  const data = await request<unknown>("/auth/welcome/complete", {
    method: "POST",
  });
  return userSchema.parse(data);
}

export function getGoogleLoginUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  return `${apiUrl}/api/v1/auth/google/login`;
}

export { AuthApiError };
