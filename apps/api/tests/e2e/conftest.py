"""E2E fixtures — real PostgreSQL + real FastAPI routes."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from tests.e2e.harness import (
    ValidationReport,
    database_reachable,
    issue_access_token,
    seed_user,
    unique_suffix,
)


@pytest.fixture(scope="module")
def require_database() -> None:
    if not database_reachable():
        pytest.skip("PostgreSQL is not reachable — skipping placement drive E2E")


@pytest.fixture(scope="module")
def run_id() -> str:
    return unique_suffix()


@pytest.fixture(scope="module")
def report(run_id: str) -> ValidationReport:
    return ValidationReport(run_id=run_id)


@pytest.fixture(scope="module")
def app_client(require_database: None, monkeypatch_module: pytest.MonkeyPatch):
    # Avoid noisy/fragile startup probes failing the suite.
    import main as main_module

    monkeypatch_module.setattr(main_module, "log_startup_diagnostics", lambda: None)
    application = main_module.create_app()
    with TestClient(application) as client:
        yield client


@pytest.fixture(scope="module")
def monkeypatch_module():
    """Module-scoped monkeypatch (pytest's monkeypatch is function-scoped)."""
    from _pytest.monkeypatch import MonkeyPatch

    mp = MonkeyPatch()
    yield mp
    mp.undo()


@pytest.fixture(scope="module")
def actors(require_database: None, run_id: str, app_client: TestClient):
    from app.database.session import SessionLocal

    db = SessionLocal()
    try:
        admin = seed_user(
            db,
            email=f"sa.{run_id}@nitrr.ac.in",
            role="SUPER_ADMIN",
            first_name="Super",
            last_name="Admin",
        )
        cell = seed_user(
            db,
            email=f"cell.{run_id}@nitrr.ac.in",
            role="PLACEMENT_CELL",
            first_name="Placement",
            last_name="Cell",
        )
        convener = seed_user(
            db,
            email=f"convener.{run_id}@nitrr.ac.in",
            role="PLACEMENT_CONVENER",
            first_name="Drive",
            last_name="Convener",
        )
        student = seed_user(
            db,
            email=f"student.{run_id}@nitrr.ac.in",
            role="STUDENT",
            first_name="Ada",
            last_name="Student",
        )
        tokens = {
            "admin": issue_access_token(db, admin),
            "cell": issue_access_token(db, cell),
            "convener": issue_access_token(db, convener),
            "student": issue_access_token(db, student),
        }
        return {
            "admin_id": admin.id,
            "cell_id": cell.id,
            "convener_id": convener.id,
            "student_id": student.id,
            "tokens": tokens,
            "client": app_client,
            "run_id": run_id,
        }
    finally:
        db.close()
