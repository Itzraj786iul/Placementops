import { apiRequest } from "@/lib/api-client";

export type SettingMeta = {
  updated_at: string | null;
  updated_by: string | null;
};

export type AdminSettingsResponse = {
  settings: Record<string, unknown>;
  meta: Record<string, SettingMeta>;
  sections: Record<string, string[]>;
  sensitive_keys: string[];
  integrations: {
    storage: {
      configured: boolean;
      cloud_name: string | null;
      status: string;
      upload_limits_mb: Record<string, number>;
      allowed_extensions: Record<string, string[]>;
    };
    authentication: {
      google_oauth_env_configured: boolean;
      env_allowed_email_domain: string;
      access_token_expire_minutes: number;
    };
    notifications: {
      email_configured: boolean;
      email_provider: string;
      email_from: string;
      template_previews: string[];
    };
    security: {
      password_policy: string;
      rate_limit_status: string;
      audit_logging_status: string;
      environment_mode: string;
    };
  };
};

export async function fetchAdminSettings(): Promise<AdminSettingsResponse> {
  return apiRequest("/admin/settings");
}

export async function patchAdminSettings(payload: {
  settings: Record<string, unknown>;
  confirm_sensitive?: boolean;
}): Promise<AdminSettingsResponse> {
  return apiRequest("/admin/settings", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}
