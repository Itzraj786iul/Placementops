import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

import { getPostAuthPath } from "@/lib/auth/redirects";
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
    let message = "Authentication failed. Please try again.";
    try {
      const body = (await exchangeResponse.json()) as { message?: string };
      if (body.message) message = body.message;
    } catch {
      // keep default
    }
    if (
      message.toLowerCase().includes("inactive") ||
      message.toLowerCase().includes("not allowed")
    ) {
      return NextResponse.redirect(
        new URL(
          `/account-inactive?message=${encodeURIComponent(message)}`,
          request.url,
        ),
      );
    }
    return NextResponse.redirect(
      new URL(`/login?error=${encodeURIComponent(message)}`, request.url),
    );
  }

  const tokens = authTokensSchema.parse(await exchangeResponse.json());
  const redirectPath = getPostAuthPath(tokens.user, tokens.is_new_user);

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
