from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.admin.feature_flag_models import FeatureFlag
from app.modules.users.models import User


class FeatureFlagRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_all(self) -> list[FeatureFlag]:
        return list(
            self.db.scalars(select(FeatureFlag).order_by(FeatureFlag.key)),
        )

    def get_by_key(self, key: str) -> FeatureFlag | None:
        return self.db.scalar(
            select(FeatureFlag).where(FeatureFlag.key == key),
        )

    def upsert(
        self,
        *,
        key: str,
        name: str,
        description: str | None,
        enabled: bool,
        scope: str,
        metadata: dict[str, Any] | None,
        updated_by: uuid.UUID,
    ) -> FeatureFlag:
        row = self.get_by_key(key)
        if row is None:
            row = FeatureFlag(
                key=key,
                name=name,
                description=description,
                enabled=enabled,
                scope=scope,
                metadata_=metadata or {},
                updated_by=updated_by,
            )
            self.db.add(row)
        else:
            row.name = name
            row.description = description
            row.enabled = enabled
            row.scope = scope
            row.metadata_ = metadata
            row.updated_by = updated_by
        return row

    def user_email(self, user_id: uuid.UUID | None) -> str | None:
        if user_id is None:
            return None
        user = self.db.get(User, user_id)
        return user.college_email if user else None
