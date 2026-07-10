import { Skeleton } from "@/components/ui/skeleton";

export function OperationsHeaderSkeleton() {
  return (
    <div className="space-y-3 border-b px-6 py-4">
      <Skeleton className="h-8 w-72" />
      <Skeleton className="h-4 w-48" />
    </div>
  );
}

export function SummaryCardsSkeleton() {
  return (
    <div className="grid gap-4 px-6 py-4 sm:grid-cols-2 lg:grid-cols-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} className="h-24 rounded-lg" />
      ))}
    </div>
  );
}

export function ApplicationTableSkeleton() {
  return (
    <div className="space-y-2 p-4">
      {Array.from({ length: 6 }).map((_, i) => (
        <Skeleton key={i} className="h-12 w-full" />
      ))}
    </div>
  );
}

export function TabPanelSkeleton() {
  return (
    <div className="space-y-4 p-6">
      {Array.from({ length: 4 }).map((_, i) => (
        <Skeleton key={i} className="h-16 w-full" />
      ))}
    </div>
  );
}
