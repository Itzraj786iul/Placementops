import { apiRequest } from "@/lib/api-client";

export type HealthLevel = "healthy" | "warning" | "critical";
export type ComponentStatus =
  "healthy" | "warning" | "critical" | "unknown" | "skipped";

export type SystemHealthResponse = {
  overall_status: HealthLevel;
  checked_at: string;
  cached: boolean;
  check_duration_ms: number;
  database: {
    status: ComponentStatus;
    connected: boolean;
    response_time_ms: number | null;
    migration_version: string | null;
    active_connections: number | null;
    detail?: string | null;
  };
  storage: {
    status: ComponentStatus;
    provider: string;
    configured: boolean;
    reachable: boolean | null;
    upload_test: string;
    detail?: string | null;
  };
  email: {
    status: ComponentStatus;
    provider: string;
    configured: boolean;
    reachable: boolean | null;
    last_send_status: string | null;
    template_count: number;
    detail?: string | null;
  };
  authentication: {
    status: ComponentStatus;
    google_oauth_configured: boolean;
    google_oauth_reachable: boolean | null;
    jwt_status: ComponentStatus;
    session_store_status: ComponentStatus;
    detail?: string | null;
  };
  application: {
    status: ComponentStatus;
    version: string;
    environment: string;
    build_date: string | null;
    git_commit: string | null;
    uptime_seconds: number;
  };
  statistics: {
    users: number;
    students: number;
    conveners: number;
    companies: number;
    hiring_opportunities: number;
    applications: number;
    notifications: number;
    storage_files_approx: number;
  };
  notes: string[];
};

export async function fetchSystemHealth(): Promise<SystemHealthResponse> {
  return apiRequest("/admin/system-health");
}
