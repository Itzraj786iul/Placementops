type WorkspaceShellProps = {
  title: string;
  description: string;
};

export function WorkspaceShell({ title, description }: WorkspaceShellProps) {
  return (
    <div className="flex flex-col gap-4">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        <p className="text-muted-foreground">{description}</p>
      </div>
      <div className="text-muted-foreground rounded-lg border border-dashed p-12 text-center text-sm">
        Workspace content will appear here.
      </div>
    </div>
  );
}
