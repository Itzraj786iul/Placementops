type PortalHeaderProps = {
  onRefresh?: () => void;
  isRefreshing?: boolean;
};

export function PortalHeader({ onRefresh, isRefreshing }: PortalHeaderProps) {
  return (
    <header className="bg-background border-b px-6 py-4">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">
            Placement Opportunities
          </h1>
          <p className="text-muted-foreground text-sm">
            Browse active campus opportunities.
          </p>
        </div>
        {onRefresh && (
          <button
            type="button"
            onClick={onRefresh}
            disabled={isRefreshing}
            className="hover:bg-accent shrink-0 rounded-md border px-3 py-1.5 text-sm disabled:opacity-50"
            aria-label="Refresh opportunities"
          >
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </button>
        )}
      </div>
    </header>
  );
}
