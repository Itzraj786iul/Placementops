from app.platform.exceptions import ApplicationError


class AuditModuleError(ApplicationError):
    pass


class AuditForbiddenError(AuditModuleError):
    def __init__(self, message: str = "Staff access required") -> None:
        super().__init__(message, status_code=403)


class AuditValidationError(AuditModuleError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)
