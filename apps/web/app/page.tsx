import { GraduationCap, Shield, Users } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-2 font-semibold">
            <GraduationCap className="text-primary h-6 w-6" />
            <span>PlacementOS</span>
          </div>
          <Button asChild>
            <Link href="/login">Sign in</Link>
          </Button>
        </div>
      </header>

      <main className="flex flex-1 flex-col items-center justify-center px-6 py-24">
        <div className="mx-auto max-w-3xl text-center">
          <p className="text-muted-foreground text-sm font-medium tracking-wide uppercase">
            National Institute of Technology, Raipur
          </p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight sm:text-5xl">
            Campus Recruitment Management
          </h1>
          <p className="text-muted-foreground mt-6 text-lg">
            PlacementOS streamlines placement operations for NIT Raipur. Manage
            drives, track applications, and coordinate between students and
            recruiters — all in one platform.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Button asChild size="lg">
              <Link href="/login">Sign in</Link>
            </Button>
            <Button asChild size="lg" variant="outline">
              <Link href="/register">Create account</Link>
            </Button>
          </div>
          <p className="text-muted-foreground mt-4 text-xs">
            @nitrr.ac.in accounts only. Sign in with Google or email and
            password — same account, same workspace.
          </p>
        </div>

        <div className="mx-auto mt-24 grid max-w-4xl gap-8 sm:grid-cols-3">
          <div className="rounded-lg border p-6 text-center">
            <Shield className="text-primary mx-auto h-8 w-8" />
            <h3 className="mt-4 font-semibold">Secure Access</h3>
            <p className="text-muted-foreground mt-2 text-sm">
              Institutional Google or email/password with role-based
              permissions.
            </p>
          </div>
          <div className="rounded-lg border p-6 text-center">
            <Users className="text-primary mx-auto h-8 w-8" />
            <h3 className="mt-4 font-semibold">Role-Based Workspaces</h3>
            <p className="text-muted-foreground mt-2 text-sm">
              Students, conveners, placement cell, and admins land in the right
              workspace automatically.
            </p>
          </div>
          <div className="rounded-lg border p-6 text-center">
            <GraduationCap className="text-primary mx-auto h-8 w-8" />
            <h3 className="mt-4 font-semibold">Built for NITRR</h3>
            <p className="text-muted-foreground mt-2 text-sm">
              Purpose-built for National Institute of Technology, Raipur.
            </p>
          </div>
        </div>
      </main>

      <footer className="text-muted-foreground border-t py-6 text-center text-sm">
        PlacementOS &copy; {new Date().getFullYear()} — NIT Raipur
      </footer>
    </div>
  );
}
