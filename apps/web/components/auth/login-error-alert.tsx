import { AlertCircle } from "lucide-react";

type LoginErrorAlertProps = {
  message: string;
};

function friendlyAuthMessage(raw: string): string {
  const decoded = decodeURIComponent(raw.replace(/\+/g, " ")).trim();
  const lower = decoded.toLowerCase();

  if (
    lower.includes("not associated with nit raipur") ||
    lower.includes("institutional emails") ||
    lower.includes("nitrr")
  ) {
    return "This Google account is not associated with NIT Raipur.";
  }
  if (lower.includes("inactive") || lower.includes("not allowed to sign in")) {
    return "Your account is currently inactive. Please contact the Placement Cell.";
  }
  if (lower.includes("google sign-in is not configured")) {
    return "Google sign-in is temporarily unavailable. Please contact the Placement Cell.";
  }
  if (lower.includes("incomplete")) {
    return "We could not read your Google account details. Please try again.";
  }
  return decoded || "Unable to sign in. Please try again.";
}

export function LoginErrorAlert({ message }: LoginErrorAlertProps) {
  const display = friendlyAuthMessage(message);

  return (
    <div
      className="border-destructive/50 bg-destructive/10 text-destructive flex items-start gap-3 rounded-lg border p-4 text-sm"
      role="alert"
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <p>{display}</p>
    </div>
  );
}
