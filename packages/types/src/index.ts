export type ApiResponse<T> = {
  data: T;
  message?: string;
};

export type PaginatedResponse<T> = {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
};

export type HealthCheckResponse = {
  status: string;
};

export type RoleName =
  "SUPER_ADMIN" | "PLACEMENT_CELL" | "PLACEMENT_CONVENER" | "STUDENT";

export type Role = {
  id: string;
  name: RoleName;
  description: string;
};

export type User = {
  id: string;
  college_email: string;
  personal_email: string | null;
  first_name: string;
  last_name: string;
  profile_picture: string | null;
  is_active: boolean;
  roles: Role[];
  last_login: string | null;
  created_at: string;
};

export type AuthTokens = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
};

export type MessageResponse = {
  message: string;
};

export type ApiErrorResponse = {
  message: string;
};
