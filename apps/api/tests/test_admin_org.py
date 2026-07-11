from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from app.modules.admin.exceptions import AdminValidationError
from app.modules.admin.org_schemas import (
    AdminDepartmentCreate,
    AdminSeasonCreate,
    SeasonActivateRequest,
    pages,
)
from app.modules.admin.org_service import AdminOrgService
from app.modules.seasons.models import (
    SEASON_STATUS_ACTIVE,
    SEASON_STATUS_PLANNING,
    SEASON_STATUSES,
)


def _actor(*role_names: str) -> SimpleNamespace:
    return SimpleNamespace(
        id=uuid4(),
        roles=[SimpleNamespace(name=r) for r in role_names],
    )


def test_season_statuses() -> None:
    assert SEASON_STATUS_ACTIVE in SEASON_STATUSES
    assert "planning" in SEASON_STATUSES
    assert "completed" in SEASON_STATUSES
    assert "archived" in SEASON_STATUSES


def test_pages_helper() -> None:
    assert pages(0, 20) == 0
    assert pages(1, 20) == 1
    assert pages(21, 20) == 2


def test_create_department_rejects_duplicate_code() -> None:
    db = MagicMock()
    service = AdminOrgService(db)
    service.repository = MagicMock()
    service.repository.get_department_by_code.return_value = object()
    service.repository.get_department_by_name.return_value = None

    with pytest.raises(AdminValidationError, match="unique"):
        service.create_department(
            _actor("SUPER_ADMIN"),
            AdminDepartmentCreate(name="CSE", code="CSE"),
        )


def test_create_season_rejects_active_status() -> None:
    db = MagicMock()
    service = AdminOrgService(db)
    service.repository = MagicMock()

    with pytest.raises(AdminValidationError, match="activate"):
        service.create_season(
            _actor("PLACEMENT_CELL"),
            AdminSeasonCreate(
                name="2026",
                academic_batch="2022-2026",
                start_date=date(2025, 7, 1),
                end_date=date(2026, 6, 30),
                status=SEASON_STATUS_ACTIVE,
            ),
        )


def test_create_season_rejects_inverted_dates() -> None:
    db = MagicMock()
    service = AdminOrgService(db)
    service.repository = MagicMock()

    with pytest.raises(AdminValidationError, match="end_date"):
        service.create_season(
            _actor("SUPER_ADMIN"),
            AdminSeasonCreate(
                name="2026",
                academic_batch="2022-2026",
                start_date=date(2026, 6, 30),
                end_date=date(2025, 7, 1),
                status=SEASON_STATUS_PLANNING,
            ),
        )


def test_activate_requires_confirm() -> None:
    db = MagicMock()
    service = AdminOrgService(db)
    service.repository = MagicMock()

    with pytest.raises(AdminValidationError, match="confirm"):
        service.activate_season(
            _actor("SUPER_ADMIN"),
            uuid4(),
            SeasonActivateRequest(confirm=False),
        )
