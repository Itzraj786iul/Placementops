from app.platform.exceptions import ApplicationError


class ApplicationModuleError(ApplicationError):
    pass


class ApplicationNotFoundError(ApplicationModuleError):
    def __init__(self, message: str = "Application not found") -> None:
        super().__init__(message, status_code=404)


class ApplicationForbiddenError(ApplicationModuleError):
    def __init__(self, message: str = "You do not have access to this application") -> None:
        super().__init__(message, status_code=403)


class ApplicationValidationError(ApplicationModuleError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class ApplicationConflictError(ApplicationModuleError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)
