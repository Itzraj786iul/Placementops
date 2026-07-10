from fastapi import Depends
from sqlalchemy.orm import Session

from app.dependencies.database import get_db_session
from app.platform.notifications.notification_service import NotificationService


def get_notification_service(
    db: Session = Depends(get_db_session),
) -> NotificationService:
    return NotificationService(db)
