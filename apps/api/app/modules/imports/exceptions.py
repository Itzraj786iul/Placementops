from app.platform.exceptions import ApplicationError


class ImportModuleError(ApplicationError):
    pass


class ImportForbiddenError(ImportModuleError):
    def __init__(self, message: str = "Staff access required") -> None:
        super().__init__(message, status_code=403)


class ImportNotFoundError(ImportModuleError):
    def __init__(self, message: str = "Import not found") -> None:
        super().__init__(message, status_code=404)


class ImportValidationError(ImportModuleError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)
