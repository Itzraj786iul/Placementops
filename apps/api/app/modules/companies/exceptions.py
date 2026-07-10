from app.platform.exceptions import ApplicationError


class CompanyError(ApplicationError):
    pass


class CompanyNotFoundError(CompanyError):
    def __init__(self, message: str = "Company not found") -> None:
        super().__init__(message, status_code=404)


class CompanyConflictError(CompanyError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)


class CompanyForbiddenError(CompanyError):
    def __init__(self, message: str = "Staff access required") -> None:
        super().__init__(message, status_code=403)


class CompanyValidationError(CompanyError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)
