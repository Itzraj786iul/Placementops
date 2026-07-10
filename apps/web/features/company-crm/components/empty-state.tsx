type CrmEmptyStateProps = {
  title: string;
  description: string;
  action?: React.ReactNode;
};

export function CrmEmptyState({
  title,
  description,
  action,
}: CrmEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed px-6 py-12 text-center">
      <div className="bg-muted text-muted-foreground mb-3 flex h-12 w-12 items-center justify-center rounded-full">
        <span className="text-lg" aria-hidden="true">
          ○
        </span>
      </div>
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="text-muted-foreground mt-1 max-w-sm text-sm">
        {description}
      </p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
