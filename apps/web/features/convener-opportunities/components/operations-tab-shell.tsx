"use client";

import * as React from "react";

import { cn } from "@/lib/utils";
import type { OperationsTab } from "@/features/convener-opportunities/types";

const TABS: { id: OperationsTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "applications", label: "Applications" },
  { id: "screening", label: "Screening" },
  { id: "documents", label: "Documents" },
  { id: "timeline", label: "Timeline" },
];

type OperationsTabShellProps = {
  activeTab: OperationsTab;
  onTabChange: (tab: OperationsTab) => void;
  applicationCount?: number;
  children: React.ReactNode;
};

export function OperationsTabShell({
  activeTab,
  onTabChange,
  applicationCount,
  children,
}: OperationsTabShellProps) {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div
        role="tablist"
        aria-label="Opportunity operations tabs"
        className="flex gap-1 overflow-x-auto border-b px-4"
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "shrink-0 px-3 py-2.5 text-sm font-medium transition-colors",
              "hover:text-foreground focus-visible:ring-ring focus-visible:ring-2 focus-visible:outline-none",
              activeTab === tab.id
                ? "border-primary text-foreground border-b-2"
                : "text-muted-foreground",
            )}
          >
            {tab.label}
            {tab.id === "applications" && applicationCount != null && (
              <span className="text-muted-foreground ml-1.5 text-xs">
                ({applicationCount})
              </span>
            )}
          </button>
        ))}
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto" role="tabpanel">
        {children}
      </div>
    </div>
  );
}

export function useLazyOperationsTab(
  activeTab: OperationsTab,
  tab: OperationsTab,
) {
  const [visited, setVisited] = React.useState(activeTab === tab);

  React.useEffect(() => {
    if (activeTab === tab) setVisited(true);
  }, [activeTab, tab]);

  return visited;
}
