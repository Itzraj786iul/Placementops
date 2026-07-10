"use client";

import * as React from "react";

import { cn } from "@/lib/utils";
import type { CrmTab } from "@/features/company-crm/types";

const TABS: { id: CrmTab; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "contacts", label: "Contacts" },
  { id: "timeline", label: "Timeline" },
  { id: "documents", label: "Documents" },
  { id: "history", label: "History" },
];

type CompanyDetailProps = {
  companyName: string | null;
  activeTab: CrmTab;
  onTabChange: (tab: CrmTab) => void;
  children: React.ReactNode;
};

export function CompanyDetail({
  companyName,
  activeTab,
  onTabChange,
  children,
}: CompanyDetailProps) {
  if (!companyName) {
    return (
      <div className="flex h-full items-center justify-center p-8 text-center">
        <p className="text-muted-foreground text-sm">
          Select a company to view details
        </p>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b px-4 py-3">
        <h2 className="font-semibold">{companyName}</h2>
      </div>
      <div
        role="tablist"
        aria-label="Company detail tabs"
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

export function useLazyTab(activeTab: CrmTab, tab: CrmTab) {
  const [visited, setVisited] = React.useState(activeTab === tab);

  React.useEffect(() => {
    if (activeTab === tab) setVisited(true);
  }, [activeTab, tab]);

  return visited;
}
