import { AlertCircle } from "lucide-react";

type LoginErrorAlertProps = {
  message: string;
};

export function LoginErrorAlert({ message }: LoginErrorAlertProps) {
  const decodedMessage = decodeURIComponent(message.replace(/\+/g, " "));

  return (
    <div
      className="border-destructive/50 bg-destructive/10 text-destructive flex items-start gap-3 rounded-lg border p-4 text-sm"
      role="alert"
    >
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
      <p>{decodedMessage}</p>
    </div>
  );
}
