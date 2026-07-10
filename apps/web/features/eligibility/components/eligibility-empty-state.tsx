type EligibilityEmptyStateProps = {
  title: string;
  description: string;
};

export function EligibilityEmptyState({
  title,
  description,
}: EligibilityEmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed px-4 py-8 text-center">
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="text-muted-foreground mt-1 text-sm">{description}</p>
    </div>
  );
}
