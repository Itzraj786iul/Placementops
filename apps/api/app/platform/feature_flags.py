"""Lightweight helper for future call sites — prefer FeatureFlagService in requests."""

from sqlalchemy.orm import Session

from app.modules.admin.feature_flag_service import FeatureFlagService


def is_enabled(db: Session, flag_key: str) -> bool:
    return FeatureFlagService(db).is_enabled(flag_key)
