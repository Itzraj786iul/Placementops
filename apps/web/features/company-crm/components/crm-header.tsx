"use client";

import { Plus, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import { SearchBar } from "@/features/company-crm/components/search-bar";

type CrmHeaderProps = {
  search: string;
  onSearchChange: (value: string) => void;
  onRefresh: () => void;
  onNewCompany: () => void;
  isRefreshing: boolean;
};

export function CrmHeader({
  search,
  onSearchChange,
  onRefresh,
  onNewCompany,
  isRefreshing,
}: CrmHeaderProps) {
  return (
    <header className="bg-background flex flex-col gap-4 border-b px-4 py-4 lg:flex-row lg:items-center lg:justify-between">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Company CRM</h1>
        <p className="text-muted-foreground text-sm">
          Manage companies, handlers and communication.
        </p>
      </div>
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
        <SearchBar
          value={search}
          onChange={onSearchChange}
          className="w-full sm:w-64"
        />
        <div className="flex gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onRefresh}
            disabled={isRefreshing}
            aria-label="Refresh companies"
          >
            <RefreshCw className={isRefreshing ? "animate-spin" : undefined} />
            Refresh
          </Button>
          <Button type="button" size="sm" onClick={onNewCompany}>
            <Plus />
            New Company
          </Button>
        </div>
      </div>
    </header>
  );
}
