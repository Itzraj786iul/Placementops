from app.platform.exceptions import ApplicationError


class EligibilityModuleError(ApplicationError):
    pass


class EligibilityNotFoundError(EligibilityModuleError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message, status_code=404)


class EligibilityForbiddenError(EligibilityModuleError):
    def __init__(self, message: str = "You do not have access to this resource") -> None:
        super().__init__(message, status_code=403)
