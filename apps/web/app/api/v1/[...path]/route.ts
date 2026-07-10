import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";

const API_URL =
  process.env.INTERNAL_API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "http://localhost:8000";

const ACCESS_TOKEN_MAX_AGE = 15 * 60;
const REFRESH_TOKEN_MAX_AGE = 7 * 24 * 60 * 60;

const AUTH_COOKIE_PATHS = new Set([
  "auth/dev/login",
  "auth/exchange",
  "auth/refresh",
]);

function setAuthCookies(
  response: NextResponse,
  tokens: {
    access_token: string;
    refresh_token: string;
  },
) {
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
}

async function refreshAccessToken(
  refreshToken: string,
): Promise<{ access_token: string; refresh_token: string } | null> {
  try {
    const refreshResponse = await fetch(`${API_URL}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!refreshResponse.ok) return null;

    return refreshResponse.json() as Promise<{
      access_token: string;
      refresh_token: string;
    }>;
  } catch {
    return null;
  }
}

function backendUnavailableResponse() {
  return NextResponse.json(
    {
      message:
        "API is unreachable. Start the backend with .\\scripts\\start-api.ps1 (http://localhost:8000).",
    },
    { status: 503 },
  );
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
): Promise<NextResponse> {
  const targetPath = pathSegments.join("/");
  const targetUrl = `${API_URL}/api/v1/${targetPath}${request.nextUrl.search}`;

  let accessToken = request.cookies.get("access_token")?.value;
  const refreshToken = request.cookies.get("refresh_token")?.value;
  let refreshedTokens: { access_token: string; refresh_token: string } | null =
    null;

  if (
    !accessToken &&
    refreshToken &&
    targetPath !== "auth/refresh" &&
    !AUTH_COOKIE_PATHS.has(targetPath)
  ) {
    refreshedTokens = await refreshAccessToken(refreshToken);
    if (refreshedTokens) {
      accessToken = refreshedTokens.access_token;
    }
  }

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("Content-Type", contentType);
  }
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    const isMultipart = contentType?.includes("multipart/form-data");
    init.body = isMultipart
      ? await request.arrayBuffer()
      : await request.text();
  }

  let backendResponse: Response;
  try {
    backendResponse = await fetch(targetUrl, init);
  } catch {
    return backendUnavailableResponse();
  }
  const backendContentType =
    backendResponse.headers.get("Content-Type") ?? "application/json";
  const isBinary =
    backendContentType.includes("spreadsheetml") ||
    backendContentType.includes("octet-stream") ||
    backendContentType.includes("application/zip");

  const responseBody = isBinary
    ? await backendResponse.arrayBuffer()
    : await backendResponse.text();

  const responseHeaders = new Headers({
    "Content-Type": backendContentType,
  });
  const contentDisposition = backendResponse.headers.get("Content-Disposition");
  if (contentDisposition) {
    responseHeaders.set("Content-Disposition", contentDisposition);
  }

  const response = new NextResponse(responseBody, {
    status: backendResponse.status,
    headers: responseHeaders,
  });

  if (refreshedTokens) {
    setAuthCookies(response, refreshedTokens);
  }

  if (targetPath === "auth/logout" && backendResponse.ok) {
    response.cookies.delete("access_token");
    response.cookies.delete("refresh_token");
  }

  if (
    AUTH_COOKIE_PATHS.has(targetPath) &&
    backendResponse.ok &&
    typeof responseBody === "string"
  ) {
    try {
      const tokens = JSON.parse(responseBody) as {
        access_token: string;
        refresh_token: string;
      };
      setAuthCookies(response, tokens);
    } catch {
      return response;
    }
  }

  return response;
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PUT(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function PATCH(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> },
) {
  const { path } = await context.params;
  return proxyRequest(request, path);
}
