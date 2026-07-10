type OperationsEmptyStateProps = {
  title: string;
  description: string;
};

export function OperationsEmptyState({
  title,
  description,
}: OperationsEmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed px-6 py-12 text-center">
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="text-muted-foreground mt-1 max-w-md text-sm">
        {description}
      </p>
    </div>
  );
}
