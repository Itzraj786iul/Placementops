"use client";

import { Loader2 } from "lucide-react";
import Link from "next/link";
import * as React from "react";

import { Button } from "@/components/ui/button";
import { AuthApiError, verifyEmail } from "@/services/auth-client";

type Props = { searchParams: Promise<{ token?: string }> };

export default function VerifyEmailPage({ searchParams }: Props) {
  const params = React.use(searchParams);
  const [status, setStatus] = React.useState<"loading" | "ok" | "error">(
    "loading",
  );
  const [message, setMessage] = React.useState("");

  React.useEffect(() => {
    if (!params.token) {
      setStatus("error");
      setMessage("Verification link is missing.");
      return;
    }
    void verifyEmail(params.token)
      .then((res) => {
        setStatus("ok");
        setMessage(res.message);
      })
      .catch((err) => {
        setStatus("error");
        setMessage(
          err instanceof AuthApiError ? err.message : "Unable to verify email.",
        );
      });
  }, [params.token]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4">
      <div className="bg-card w-full max-w-md space-y-4 rounded-xl border p-8 text-center shadow-sm">
        {status === "loading" && (
          <Loader2 className="text-primary mx-auto h-8 w-8 animate-spin" />
        )}
        {status !== "loading" && (
          <>
            <h1 className="text-xl font-semibold">
              {status === "ok" ? "Email verified" : "Verification failed"}
            </h1>
            <p className="text-muted-foreground text-sm">{message}</p>
            <Button asChild>
              <Link href="/login">Continue to sign in</Link>
            </Button>
          </>
        )}
      </div>
    </div>
  );
}
