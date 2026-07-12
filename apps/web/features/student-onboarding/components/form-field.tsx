"use client";

import { Label } from "@/components/ui/label";
import { cn } from "@/lib/utils";

type FormFieldProps = {
  label: string;
  htmlFor?: string;
  error?: string;
  /** When true, shows a red asterisk. When false, shows an Optional label. */
  required?: boolean;
  children: React.ReactNode;
  className?: string;
};

export function FormField({
  label,
  htmlFor,
  error,
  required,
  children,
  className,
}: FormFieldProps) {
  return (
    <div className={cn("space-y-2", className)}>
      <Label htmlFor={htmlFor} className="inline-flex items-center gap-1.5">
        <span>{label}</span>
        {required === true && (
          <span className="text-destructive" aria-hidden="true">
            *
          </span>
        )}
        {required === false && (
          <span className="text-muted-foreground text-xs font-normal">
            Optional
          </span>
        )}
      </Label>
      <div
        className={cn(
          error &&
            "[&_input]:border-destructive [&_select]:border-destructive [&_textarea]:border-destructive [&_input]:focus-visible:ring-destructive [&_select]:focus-visible:ring-destructive [&_textarea]:focus-visible:ring-destructive",
        )}
      >
        {children}
      </div>
      {error && (
        <p className="text-destructive text-xs" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
