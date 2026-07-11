"""Shared helpers for PlacementOS end-to-end workflow validation."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database.session import SessionLocal
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import CreateUserData
from app.modules.users.service import UserService
from app.platform.auth.password import hash_password
from app.platform.auth.service import AuthService


REPORT_PATH = Path(__file__).resolve().parents[4] / "docs" / "VALIDATION_REPORT.md"


@dataclass
class StepResult:
    phase: str
    name: str
    passed: bool
    duration_ms: float
    detail: str = ""
    http_status: int | None = None
    path: str | None = None


@dataclass
class ValidationReport:
    run_id: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    steps: list[StepResult] = field(default_factory=list)
    bugs: list[str] = field(default_factory=list)
    observations: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    architecture_notes: list[str] = field(default_factory=list)

    @property
    def passed(self) -> int:
        return sum(1 for s in self.steps if s.passed)

    @property
    def failed(self) -> int:
        return sum(1 for s in self.steps if not s.passed)

    @property
    def overall_pass(self) -> bool:
        return self.failed == 0 and len(self.steps) > 0

    def add(
        self,
        *,
        phase: str,
        name: str,
        passed: bool,
        duration_ms: float,
        detail: str = "",
        http_status: int | None = None,
        path: str | None = None,
    ) -> None:
        self.steps.append(
            StepResult(
                phase=phase,
                name=name,
                passed=passed,
                duration_ms=duration_ms,
                detail=detail,
                http_status=http_status,
                path=path,
            ),
        )
        if not passed:
            self.bugs.append(f"[{phase}] {name}: {detail or 'failed'}")

    def write_markdown(self, path: Path = REPORT_PATH) -> Path:
        ended = datetime.now(timezone.utc)
        total_ms = sum(s.duration_ms for s in self.steps)
        lines = [
            "# PlacementOS — Placement Drive Validation Report",
            "",
            f"**Run ID:** `{self.run_id}`  ",
            f"**Started:** {self.started_at.isoformat()}  ",
            f"**Finished:** {ended.isoformat()}  ",
            f"**Result:** {'PASS' if self.overall_pass else 'FAIL'}  ",
            f"**Steps:** {self.passed} passed / {self.failed} failed / {len(self.steps)} total  ",
            f"**Wall time (sum of steps):** {total_ms:.1f} ms",
            "",
            "## 1. Validation Report",
            "",
            "| Phase | Step | Result | Duration (ms) | Detail |",
            "| ----- | ---- | ------ | ------------- | ------ |",
        ]
        for step in self.steps:
            status = "PASS" if step.passed else "FAIL"
            detail = (step.detail or "").replace("|", "\\|")
            lines.append(
                f"| {step.phase} | {step.name} | {status} | {step.duration_ms:.1f} | {detail} |",
            )

        lines.extend(
            [
                "",
                "## 2. Pass / Fail",
                "",
                f"**Overall: {'PASS' if self.overall_pass else 'FAIL'}**",
                "",
                "## 3. Performance observations",
                "",
            ],
        )
        if self.observations:
            lines.extend(f"- {item}" for item in self.observations)
        else:
            lines.append("- No performance anomalies recorded beyond per-step timings above.")

        slow = sorted(self.steps, key=lambda s: s.duration_ms, reverse=True)[:5]
        if slow:
            lines.append("")
            lines.append("Slowest steps:")
            for step in slow:
                lines.append(f"- {step.phase} / {step.name}: {step.duration_ms:.1f} ms")

        lines.extend(["", "## 4. Architecture observations", ""])
        if self.architecture_notes:
            lines.extend(f"- {item}" for item in self.architecture_notes)
        else:
            lines.append("- Workflow exercised Router → Service → Repository via HTTP `/api/v1`.")

        lines.extend(["", "## 5. Bugs discovered", ""])
        if self.bugs:
            lines.extend(f"- {item}" for item in self.bugs)
        else:
            lines.append("- None in this run.")

        lines.extend(["", "## 6. Recommendations before v1.0", ""])
        if self.recommendations:
            lines.extend(f"- {item}" for item in self.recommendations)
        else:
            lines.append("- Re-run this suite against staging with Cloudinary + Resend enabled before go-live.")

        lines.append("")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


class ApiSession:
    """Thin HTTP client that always hits real FastAPI routes."""

    def __init__(self, client: TestClient, access_token: str | None = None) -> None:
        self.client = client
        self.access_token = access_token

    def as_user(self, access_token: str) -> ApiSession:
        return ApiSession(self.client, access_token)

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any = None,
        data: Any = None,
        files: Any = None,
        params: dict | None = None,
    ) -> Any:
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        return self.client.request(
            method,
            path,
            json=json,
            data=data,
            files=files,
            params=params,
            headers=headers,
        )


def database_reachable() -> bool:
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return True
        finally:
            db.close()
    except Exception:  # noqa: BLE001
        return False


def seed_user(
    db: Session,
    *,
    email: str,
    role: str,
    first_name: str,
    last_name: str,
    password: str = "PlacementDrive!2026",
) -> Any:
    repo = UserRepository(db)
    repo.seed_roles()
    users = UserService(db)
    existing = users.get_by_college_email(email)
    if existing is not None:
        role_row = repo.get_role_by_name(role)
        if role_row is None:
            raise RuntimeError(f"Role {role} missing")
        repo.clear_roles(existing.id)
        repo.assign_role(existing.id, role_row.id)
        repo.set_password_hash(existing, hash_password(password))
        db.commit()
        return users.get_by_id(existing.id)

    user = users.create_user(
        CreateUserData(
            college_email=email,
            personal_email=None,
            first_name=first_name,
            last_name=last_name,
            display_name=f"{first_name} {last_name}",
            email_verified=True,
        ),
    )
    role_row = repo.get_role_by_name(role)
    if role_row is None:
        raise RuntimeError(f"Role {role} missing")
    repo.clear_roles(user.id)
    repo.assign_role(user.id, role_row.id)
    repo.set_password_hash(user, hash_password(password))
    db.commit()
    return users.get_by_id(user.id)


def issue_access_token(db: Session, user: Any) -> str:
    tokens = AuthService(db).create_tokens(user)
    return tokens.access_token


def timed_step(
    report: ValidationReport,
    *,
    phase: str,
    name: str,
    fn,
) -> Any:
    started = time.perf_counter()
    try:
        result = fn()
        duration = (time.perf_counter() - started) * 1000
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], dict):
            value, meta = result
            report.add(
                phase=phase,
                name=name,
                passed=True,
                duration_ms=duration,
                detail=str(meta.get("detail", "")),
                http_status=meta.get("status"),
                path=meta.get("path"),
            )
            return value
        report.add(phase=phase, name=name, passed=True, duration_ms=duration)
        return result
    except Exception as exc:  # noqa: BLE001 — capture for report
        duration = (time.perf_counter() - started) * 1000
        report.add(
            phase=phase,
            name=name,
            passed=False,
            duration_ms=duration,
            detail=f"{type(exc).__name__}: {exc}",
        )
        raise


def expect_ok(response, *, path: str, allow: set[int] | None = None) -> dict | list | bytes | None:
    allowed = allow or {200, 201, 204}
    if response.status_code not in allowed:
        body = response.text[:500]
        raise AssertionError(f"{path} -> {response.status_code}: {body}")
    if response.status_code == 204 or not response.content:
        return None
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()
    return response.content


def unique_suffix() -> str:
    return uuid.uuid4().hex[:8]
