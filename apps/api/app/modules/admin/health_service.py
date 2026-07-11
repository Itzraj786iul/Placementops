from __future__ import annotations

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.modules.admin.access import ensure_super_admin
from app.modules.admin.health_cache import get_cached_health, set_cached_health
from app.modules.admin.health_schemas import (
    ApplicationInfo,
    AuthHealth,
    ComponentStatus,
    DatabaseHealth,
    EmailHealth,
    HealthLevel,
    StorageHealth,
    SystemHealthResponse,
    SystemStatistics,
)
from app.modules.applications.models import Application
from app.modules.companies.models import Company
from app.modules.hiring_opportunities.models import HiringOpportunity
from app.modules.students.models import StudentDocument, StudentProfile, StudentResumeLibrary
from app.modules.users.models import Role, User, UserRole
from app.platform.notifications.models import Notification
from app.platform.notifications.template_service import TemplateService
from app.utils.datetime import utc_now

_PROCESS_STARTED_AT = time.monotonic()


def _environment_mode() -> str:
    if settings.ENABLE_DEV_LOGIN:
        return "development"
    if settings.COOKIE_SECURE:
        return "production"
    return (os.getenv("ENVIRONMENT") or "local").lower()


def _git_commit() -> str | None:
    for key in ("GIT_COMMIT", "RENDER_GIT_COMMIT", "COMMIT_SHA", "SOURCE_VERSION"):
        value = os.getenv(key, "").strip()
        if value:
            return value[:40]
    return None


def _build_date() -> str | None:
    for key in ("BUILD_DATE", "RENDER_BUILD_TIME"):
        value = os.getenv(key, "").strip()
        if value:
            return value
    return None


def _google_oauth_configured() -> bool:
    client_id = settings.GOOGLE_CLIENT_ID.strip()
    client_secret = settings.GOOGLE_CLIENT_SECRET.strip()
    if not client_id or not client_secret:
        return False
    if "****" in client_id or "****" in client_secret:
        return False
    if "your-" in client_id.lower() or "your-" in client_secret.lower():
        return False
    return len(client_secret) >= 16


def _jwt_status() -> ComponentStatus:
    secret = settings.JWT_SECRET_KEY.strip()
    if not secret or secret == "change-me-in-production-use-a-long-random-secret":
        return "warning"
    if len(secret) < 32:
        return "warning"
    return "healthy"


def _http_reachable(url: str, *, timeout: float = 1.5) -> bool:
    try:
        req = Request(url, method="HEAD", headers={"User-Agent": "PlacementOS-Health/1.0"})
        with urlopen(req, timeout=timeout) as resp:  # noqa: S310 — fixed HTTPS endpoints only
            return 200 <= getattr(resp, "status", 0) < 500
    except (URLError, OSError, ValueError, TimeoutError):
        try:
            req = Request(url, method="GET", headers={"User-Agent": "PlacementOS-Health/1.0"})
            with urlopen(req, timeout=timeout) as resp:  # noqa: S310
                return 200 <= getattr(resp, "status", 0) < 500
        except (URLError, OSError, ValueError, TimeoutError):
            return False


def _cloudinary_ping() -> tuple[bool | None, str | None]:
    if not settings.cloudinary_configured:
        return None, "Cloudinary not configured"
    try:
        import cloudinary
        import cloudinary.api

        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        result = cloudinary.api.ping()
        status = str(result.get("status", "")).lower() if isinstance(result, dict) else ""
        if status in {"ok", "pong"} or result:
            return True, None
        return False, "Unexpected ping response"
    except Exception as exc:  # noqa: BLE001 — health must not raise
        return False, type(exc).__name__


def _worst(*statuses: ComponentStatus) -> HealthLevel:
    if "critical" in statuses:
        return "critical"
    if "warning" in statuses or "unknown" in statuses:
        return "warning"
    return "healthy"


class AdminHealthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_system_health(self, actor: User) -> SystemHealthResponse:
        ensure_super_admin(actor)

        cached = get_cached_health()
        if cached is not None:
            payload = SystemHealthResponse.model_validate(cached)
            payload.cached = True
            return payload

        started = time.perf_counter()
        response = self._collect()
        response.check_duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.cached = False
        set_cached_health(response.model_dump(mode="json"))
        return response

    def _collect(self) -> SystemHealthResponse:
        notes = [
            "Read-only diagnostics only — no upload/delete probes.",
            "Secrets, tokens, and credential URLs are never returned.",
        ]

        # External checks in parallel (bounded)
        external: dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {
                pool.submit(_cloudinary_ping): "cloudinary",
                pool.submit(_http_reachable, "https://accounts.google.com"): "google",
                pool.submit(
                    _http_reachable,
                    "https://api.resend.com",
                ): "resend",
            }
            for fut in as_completed(futures):
                key = futures[fut]
                try:
                    external[key] = fut.result(timeout=0.1)
                except Exception:  # noqa: BLE001
                    external[key] = None

        database = self._check_database()
        storage = self._check_storage(external.get("cloudinary"))
        email = self._check_email(external.get("resend"))
        auth = self._check_auth(
            google_reachable=external.get("google"),
            session_ok=database.connected,
        )
        application = ApplicationInfo(
            version=settings.VERSION,
            environment=_environment_mode(),
            build_date=_build_date(),
            git_commit=_git_commit(),
            uptime_seconds=int(time.monotonic() - _PROCESS_STARTED_AT),
        )
        statistics = self._statistics() if database.connected else SystemStatistics(
            users=0,
            students=0,
            conveners=0,
            companies=0,
            hiring_opportunities=0,
            applications=0,
            notifications=0,
            storage_files_approx=0,
        )

        overall = _worst(
            database.status,
            storage.status,
            email.status,
            auth.status,
        )
        if not database.connected:
            overall = "critical"

        return SystemHealthResponse(
            overall_status=overall,
            checked_at=utc_now(),
            check_duration_ms=0,
            database=database,
            storage=storage,
            email=email,
            authentication=auth,
            application=application,
            statistics=statistics,
            notes=notes,
        )

    def _check_database(self) -> DatabaseHealth:
        started = time.perf_counter()
        try:
            self.db.execute(text("SELECT 1"))
            response_ms = round((time.perf_counter() - started) * 1000, 2)

            migration_version = None
            try:
                migration_version = self.db.execute(
                    text("SELECT version_num FROM alembic_version LIMIT 1"),
                ).scalar()
            except Exception:  # noqa: BLE001
                migration_version = None

            active_connections = None
            try:
                active_connections = self.db.execute(
                    text(
                        "SELECT count(*) FROM pg_stat_activity "
                        "WHERE datname = current_database()",
                    ),
                ).scalar()
            except Exception:  # noqa: BLE001
                active_connections = None

            status: ComponentStatus = "healthy"
            if response_ms > 200:
                status = "warning"

            return DatabaseHealth(
                status=status,
                connected=True,
                response_time_ms=response_ms,
                migration_version=str(migration_version) if migration_version else None,
                active_connections=int(active_connections)
                if active_connections is not None
                else None,
            )
        except Exception as exc:  # noqa: BLE001
            return DatabaseHealth(
                status="critical",
                connected=False,
                response_time_ms=None,
                detail=type(exc).__name__,
            )

    def _check_storage(self, ping_result: Any) -> StorageHealth:
        configured = settings.cloudinary_configured
        if not configured:
            return StorageHealth(
                status="warning",
                configured=False,
                reachable=None,
                upload_test="skipped",
                detail="Not configured",
            )

        reachable: bool | None = None
        detail: str | None = None
        if isinstance(ping_result, tuple) and len(ping_result) == 2:
            reachable, detail = ping_result
        elif ping_result is None:
            reachable = None
            detail = "Ping timed out"

        if reachable is True:
            status: ComponentStatus = "healthy"
        elif reachable is False:
            status = "critical"
        else:
            status = "warning"

        return StorageHealth(
            status=status,
            configured=True,
            reachable=reachable,
            upload_test="skipped",
            detail=detail or "Upload probe disabled (read-only)",
        )

    def _check_email(self, resend_reachable: Any) -> EmailHealth:
        templates = TemplateService().available_templates()
        configured = settings.email_configured
        last_send = self._last_email_delivery_status()

        if not configured:
            return EmailHealth(
                status="warning",
                provider=settings.EMAIL_PROVIDER or "none",
                configured=False,
                reachable=None,
                last_send_status=last_send,
                template_count=len(templates),
                detail="Email provider not configured",
            )

        reachable = bool(resend_reachable) if isinstance(resend_reachable, bool) else None
        if reachable is True:
            status: ComponentStatus = "healthy"
        elif reachable is False:
            status = "warning"
        else:
            status = "warning"

        return EmailHealth(
            status=status,
            provider=settings.EMAIL_PROVIDER,
            configured=True,
            reachable=reachable,
            last_send_status=last_send,
            template_count=len(templates),
        )

    def _last_email_delivery_status(self) -> str | None:
        try:
            row = self.db.execute(
                select(Notification.delivery_status)
                .order_by(Notification.created_at.desc())
                .limit(1),
            ).scalar()
            if row is None:
                return "none"
            return row.value if hasattr(row, "value") else str(row)
        except Exception:  # noqa: BLE001
            return "unknown"

    def _check_auth(
        self,
        *,
        google_reachable: Any,
        session_ok: bool,
    ) -> AuthHealth:
        oauth_configured = _google_oauth_configured()
        jwt_status = _jwt_status()
        session_status: ComponentStatus = "healthy" if session_ok else "critical"
        google_ok = bool(google_reachable) if isinstance(google_reachable, bool) else None

        statuses: list[ComponentStatus] = [jwt_status, session_status]
        if oauth_configured and google_ok is False:
            statuses.append("warning")
        elif not oauth_configured:
            statuses.append("warning")

        overall = _worst(*statuses)
        detail_parts = []
        if not oauth_configured:
            detail_parts.append("Google OAuth env not fully configured")
        if jwt_status != "healthy":
            detail_parts.append("JWT secret should be rotated for production")

        return AuthHealth(
            status=overall,  # type: ignore[arg-type]
            google_oauth_configured=oauth_configured,
            google_oauth_reachable=google_ok if oauth_configured else None,
            jwt_status=jwt_status,
            session_store_status=session_status,
            detail="; ".join(detail_parts) if detail_parts else None,
        )

    def _statistics(self) -> SystemStatistics:
        def count(model: Any) -> int:
            return int(self.db.scalar(select(func.count()).select_from(model)) or 0)

        conveners = (
            self.db.scalar(
                select(func.count(func.distinct(UserRole.user_id)))
                .select_from(UserRole)
                .join(Role, Role.id == UserRole.role_id)
                .where(Role.name == "PLACEMENT_CONVENER"),
            )
            or 0
        )

        storage_files = count(StudentDocument) + count(StudentResumeLibrary)

        return SystemStatistics(
            users=count(User),
            students=count(StudentProfile),
            conveners=int(conveners),
            companies=count(Company),
            hiring_opportunities=count(HiringOpportunity),
            applications=count(Application),
            notifications=count(Notification),
            storage_files_approx=storage_files,
        )
