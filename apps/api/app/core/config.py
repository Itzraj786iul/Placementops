from pydantic_settings import BaseSettings, SettingsConfigDict


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

    DATABASE_URL: str = (
        "postgresql://placementos:placementos@localhost:5432/placementos"
    )

    CORS_ORIGINS: str = "http://localhost:3000"

    FRONTEND_URL: str = "http://localhost:3000"

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    ALLOWED_EMAIL_DOMAIN: str = "nitrr.ac.in"

    JWT_SECRET_KEY: str = "change-me-in-production-use-a-long-random-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    AUTH_CODE_EXPIRE_MINUTES: int = 5

    COOKIE_SECURE: bool = False
    COOKIE_DOMAIN: str | None = None

    ENABLE_DEV_LOGIN: bool = False

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "PlacementOS <onboarding@resend.dev>"
    EMAIL_PROVIDER: str = "resend"

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


settings = Settings()
