from app.platform.exceptions import ApplicationError


class UserError(ApplicationError):
    pass


class ForbiddenError(UserError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status_code=403)


class InvalidEmailDomainError(UserError):
    def __init__(self) -> None:
        super().__init__(
            "Only NITRR institutional emails (@nitrr.ac.in or @*.nitrr.ac.in) are permitted",
            status_code=403,
        )
