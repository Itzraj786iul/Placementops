"use client";

import * as React from "react";

import { cn } from "@/lib/utils";

type SlideOverProps = {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
};

export function SlideOver({
  open,
  onClose,
  title,
  description,
  children,
}: SlideOverProps) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <button
        type="button"
        className="absolute inset-0 bg-black/40"
        aria-label="Close panel"
        onClick={onClose}
      />
      <aside
        role="dialog"
        aria-modal="true"
        aria-labelledby="slide-over-title"
        className={cn(
          "bg-background relative flex h-full w-full max-w-md flex-col border-l shadow-xl",
          "animate-in slide-in-from-right duration-200",
        )}
      >
        <header className="border-b px-6 py-4">
          <h2 id="slide-over-title" className="text-lg font-semibold">
            {title}
          </h2>
          {description && (
            <p className="text-muted-foreground mt-1 text-sm">{description}</p>
          )}
        </header>
        <div className="flex-1 overflow-y-auto px-6 py-4">{children}</div>
      </aside>
    </div>
  );
}
