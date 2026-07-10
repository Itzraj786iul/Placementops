import { FileQuestion } from "lucide-react";
import Link from "next/link";

import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <AppShell>
      <div className="flex min-h-[50vh] flex-col items-center justify-center gap-4">
        <FileQuestion className="text-muted-foreground h-12 w-12" />
        <div className="text-center">
          <h2 className="text-lg font-semibold">Page not found</h2>
          <p className="text-muted-foreground text-sm">
            The page you are looking for does not exist.
          </p>
        </div>
        <Button asChild variant="outline">
          <Link href="/">Return home</Link>
        </Button>
      </div>
    </AppShell>
  );
}
