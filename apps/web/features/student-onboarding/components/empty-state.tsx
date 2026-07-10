type EmptyStateProps = {
  title: string;
  description: string;
  action?: React.ReactNode;
};

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed p-8 text-center">
      <h3 className="text-sm font-medium">{title}</h3>
      <p className="text-muted-foreground mt-1 text-sm">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
