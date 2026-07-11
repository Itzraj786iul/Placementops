from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_JWT_SECRET = "change-me-in-production-use-a-long-random-secret"


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
    # None = auto (enabled only when not production)
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
    def api_docs_enabled(self) -> bool:
        if self.ENABLE_API_DOCS is not None:
            return self.ENABLE_API_DOCS
        return not self.is_production

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

    def assert_production_security(self) -> None:
        """Fail fast when production env is unsafe for a live placement season."""
        if not self.is_production:
            return
        if self.ENABLE_DEV_LOGIN:
            raise RuntimeError(
                "ENABLE_DEV_LOGIN must be false when ENVIRONMENT=production",
            )
        if not self.COOKIE_SECURE:
            raise RuntimeError(
                "COOKIE_SECURE must be true when ENVIRONMENT=production",
            )
        secret = self.JWT_SECRET_KEY.strip()
        if not secret or secret == _DEFAULT_JWT_SECRET or len(secret) < 32:
            raise RuntimeError(
                "JWT_SECRET_KEY must be a strong secret (>=32 chars) in production",
            )


settings = Settings()
