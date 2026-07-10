import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { getWorkspacePathForUser } from "@/lib/auth/redirects";
import { authTokensSchema } from "@/lib/auth/schemas";

const API_URL =
  process.env.INTERNAL_API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

const ACCESS_TOKEN_MAX_AGE = 15 * 60;
const REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60;

export async function GET(request: NextRequest) {
  const code = request.nextUrl.searchParams.get("code");

  if (!code) {
    return NextResponse.redirect(
      new URL("/login?error=Authentication+session+is+invalid", request.url),
    );
  }

  const exchangeResponse = await fetch(`${API_URL}/api/v1/auth/exchange`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  if (!exchangeResponse.ok) {
    return NextResponse.redirect(
      new URL("/login?error=Authentication+failed", request.url),
    );
  }

  const tokens = authTokensSchema.parse(await exchangeResponse.json());
  const redirectPath = getWorkspacePathForUser(tokens.user);

  const response = NextResponse.redirect(new URL(redirectPath, request.url));
  const secure = process.env.NODE_ENV === "production";

  response.cookies.set("access_token", tokens.access_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: ACCESS_TOKEN_MAX_AGE,
  });

  response.cookies.set("refresh_token", tokens.refresh_token, {
    httpOnly: true,
    secure,
    sameSite: "lax",
    path: "/",
    maxAge: REFRESH_TOKEN_MAX_AGE,
  });

  return response;
}
