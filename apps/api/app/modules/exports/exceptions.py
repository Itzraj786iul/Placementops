from app.platform.exceptions import ApplicationError


class ExportModuleError(ApplicationError):
    pass


class ExportForbiddenError(ExportModuleError):
    def __init__(self, message: str = "Staff access required") -> None:
        super().__init__(message, status_code=403)


class ExportNotFoundError(ExportModuleError):
    def __init__(self, message: str = "Hiring opportunity not found") -> None:
        super().__init__(message, status_code=404)


class ExportValidationError(ExportModuleError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)
