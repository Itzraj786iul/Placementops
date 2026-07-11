from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.admin.settings_models import SystemSetting


class AdminSettingsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[SystemSetting]:
        return list(self.db.scalars(select(SystemSetting).order_by(SystemSetting.key)))

    def get_by_key(self, key: str) -> SystemSetting | None:
        return self.db.scalar(
            select(SystemSetting).where(SystemSetting.key == key),
        )

    def upsert(
        self,
        *,
        key: str,
        value: Any,
        updated_by: uuid.UUID,
    ) -> SystemSetting:
        row = self.get_by_key(key)
        if row is None:
            row = SystemSetting(key=key, value=value, updated_by=updated_by)
            self.db.add(row)
            self.db.flush()
        else:
            row.value = value
            row.updated_by = updated_by
        return row
