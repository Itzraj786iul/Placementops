"use client";

import * as React from "react";

import { cn } from "@/lib/utils";
import type { OpportunityTab } from "@/features/student-opportunities/types";

const TABS: { id: OpportunityTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "eligibility", label: "Eligibility" },
  { id: "documents", label: "Documents" },
  { id: "application", label: "Application" },
];

type OpportunityDetailShellProps = {
  title: string | null;
  activeTab: OpportunityTab;
  onTabChange: (tab: OpportunityTab) => void;
  children: React.ReactNode;
};

export function OpportunityDetailShell({
  title,
  activeTab,
  onTabChange,
  children,
}: OpportunityDetailShellProps) {
  if (!title) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center">
        <p className="text-muted-foreground text-sm">
          Select an opportunity to view details
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b px-4 py-3">
        <h2 className="font-semibold">{title}</h2>
      </div>
      <div
        role="tablist"
        aria-label="Opportunity detail tabs"
        className="flex gap-1 overflow-x-auto border-b px-2"
      >
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            onClick={() => onTabChange(tab.id)}
            className={cn(
              "shrink-0 px-3 py-2 text-sm font-medium transition-colors",
              "hover:text-foreground focus-visible:ring-ring focus-visible:ring-2 focus-visible:outline-none",
              activeTab === tab.id
                ? "border-primary text-foreground border-b-2"
                : "text-muted-foreground",
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="flex-1 overflow-y-auto" role="tabpanel">
        {children}
      </div>
    </div>
  );
}

export function useLazyOpportunityTab(
  activeTab: OpportunityTab,
  tab: OpportunityTab,
) {
  const [visited, setVisited] = React.useState(activeTab === tab);

  React.useEffect(() => {
    if (activeTab === tab) setVisited(true);
  }, [activeTab, tab]);

  return visited;
}
