from app.platform.exceptions import ApplicationError


class NotificationError(ApplicationError):
    pass


class NotificationNotFoundError(NotificationError):
    def __init__(self, message: str = "Notification not found") -> None:
        super().__init__(message, status_code=404)


class NotificationForbiddenError(NotificationError):
    def __init__(self, message: str = "You do not have access to this notification") -> None:
        super().__init__(message, status_code=403)
