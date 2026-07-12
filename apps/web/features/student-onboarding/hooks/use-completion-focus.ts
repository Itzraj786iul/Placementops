"use client";

import * as React from "react";

import { useOnboarding } from "@/features/student-onboarding/context/onboarding-context";

/**
 * After guided navigation, scroll to and briefly highlight the missing field/section.
 */
export function useCompletionFocus() {
  const { focusTarget, clearFocusTarget } = useOnboarding();

  React.useEffect(() => {
    if (!focusTarget) return;

    const timer = window.setTimeout(() => {
      const el = document.querySelector<HTMLElement>(
        `[data-completion-focus="${CSS.escape(focusTarget)}"]`,
      );
      if (!el) {
        clearFocusTarget();
        return;
      }

      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.add("ring-2", "ring-amber-500", "ring-offset-2");

      const focusable = el.matches("input,select,textarea,button")
        ? el
        : el.querySelector<HTMLElement>("input,select,textarea,button");
      focusable?.focus({ preventScroll: true });

      window.setTimeout(() => {
        el.classList.remove("ring-2", "ring-amber-500", "ring-offset-2");
        clearFocusTarget();
      }, 2200);
    }, 80);

    return () => window.clearTimeout(timer);
  }, [focusTarget, clearFocusTarget]);
}
