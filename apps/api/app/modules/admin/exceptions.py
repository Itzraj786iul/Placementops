from app.platform.exceptions import ApplicationError


class AdminError(ApplicationError):
    pass


class AdminForbiddenError(AdminError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status_code=403)


class AdminNotFoundError(AdminError):
    def __init__(self, message: str = "User not found") -> None:
        super().__init__(message, status_code=404)


class AdminValidationError(AdminError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)
