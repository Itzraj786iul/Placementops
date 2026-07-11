from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_JWT_SECRET = "change-me-in-production-use-a-long-random-secret"
_LOCAL_DB_MARKERS = (
    "localhost",
    "127.0.0.1",
    "placementos:placementos@",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    PROJECT_NAME: str = "PlacementOS API"
    VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    # local | development | staging | production
    ENVIRONMENT: str = "local"

    DATABASE_URL: str = (
        "postgresql://placementos:placementos@localhost:5432/placementos"
    )

    CORS_ORIGINS: str = "http://localhost:3000"

    FRONTEND_URL: str = "http://localhost:3000"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    ALLOWED_EMAIL_DOMAIN: str = "nitrr.ac.in"

    JWT_SECRET_KEY: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_CODE_EXPIRE_MINUTES: int = 5

    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None

    ENABLE_DEV_LOGIN: bool = False
    # None = auto (disabled when ENVIRONMENT is staging or production)
    ENABLE_API_DOCS: bool | None = None

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "PlacementOS <onboarding@resend.dev>"
    EMAIL_PROVIDER: str = "resend"

    @field_validator("ENVIRONMENT", mode="before")
    @classmethod
    def normalize_environment(cls, value: object) -> str:
        if value is None or value == "":
            return "local"
        return str(value).strip().lower()

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def is_deployed(self) -> bool:
        """Staging and production share HTTPS / secret hardening."""
        return self.ENVIRONMENT in {"staging", "production"}

    @property
    def api_docs_enabled(self) -> bool:
        if self.ENABLE_API_DOCS is not None:
            return self.ENABLE_API_DOCS
        return not self.is_deployed

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def cloudinary_configured(self) -> bool:
        return bool(
            self.CLOUDINARY_CLOUD_NAME.strip()
            and self.CLOUDINARY_API_KEY.strip()
            and self.CLOUDINARY_API_SECRET.strip()
            and "your-cloud" not in self.CLOUDINARY_CLOUD_NAME
            and "your-api" not in self.CLOUDINARY_API_KEY
        )

    @property
    def email_configured(self) -> bool:
        return bool(
            self.RESEND_API_KEY.strip()
            and self.EMAIL_FROM.strip()
            and "your-resend" not in self.RESEND_API_KEY.lower()
        )

    @property
    def google_oauth_configured(self) -> bool:
        client_id = self.GOOGLE_CLIENT_ID.strip()
        client_secret = self.GOOGLE_CLIENT_SECRET.strip()
        redirect = self.GOOGLE_REDIRECT_URI.strip()
        if not client_id or not client_secret or not redirect:
            return False
        lowered = f"{client_id} {client_secret}".lower()
        if "your-" in lowered or "****" in lowered:
            return False
        return len(client_secret) >= 16

    def assert_production_security(self) -> None:
        """Fail fast when staging/production env is unsafe for live traffic."""
        if not self.is_deployed:
            return

        errors: list[str] = []

        if self.ENABLE_DEV_LOGIN:
            errors.append(
                "ENABLE_DEV_LOGIN must be false when ENVIRONMENT is "
                f"{self.ENVIRONMENT}",
            )
        if not self.COOKIE_SECURE:
            errors.append(
                "COOKIE_SECURE must be true when ENVIRONMENT is "
                f"{self.ENVIRONMENT}",
            )

        secret = self.JWT_SECRET_KEY.strip()
        if not secret or secret == _DEFAULT_JWT_SECRET or len(secret) < 32:
            errors.append(
                "JWT_SECRET_KEY must be a strong secret (>=32 chars) "
                f"when ENVIRONMENT is {self.ENVIRONMENT}",
            )

        db_url = self.DATABASE_URL.strip().lower()
        if any(marker in db_url for marker in _LOCAL_DB_MARKERS):
            errors.append(
                "DATABASE_URL must point at the managed database "
                f"(not localhost) when ENVIRONMENT is {self.ENVIRONMENT}",
            )

        frontend = self.FRONTEND_URL.strip().rstrip("/")
        if not frontend.startswith("https://"):
            errors.append(
                "FRONTEND_URL must be an https:// origin when ENVIRONMENT is "
                f"{self.ENVIRONMENT}",
            )

        cors = self.cors_origins_list
        if not cors:
            errors.append("CORS_ORIGINS must include at least one frontend origin")
        else:
            normalized = {origin.rstrip("/") for origin in cors}
            if frontend and frontend not in normalized:
                errors.append(
                    "CORS_ORIGINS must include FRONTEND_URL "
                    f"({self.FRONTEND_URL})",
                )

        if not self.google_oauth_configured:
            errors.append(
                "GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and "
                "GOOGLE_REDIRECT_URI must be configured for deployed environments",
            )
        elif "localhost" in self.GOOGLE_REDIRECT_URI.lower():
            errors.append(
                "GOOGLE_REDIRECT_URI must be the public API callback URL "
                f"when ENVIRONMENT is {self.ENVIRONMENT}",
            )

        if errors:
            raise RuntimeError(
                "Deployed environment configuration is invalid:\n- "
                + "\n- ".join(errors),
            )


settings = Settings()
