from app.platform.exceptions import ApplicationError


class UserError(ApplicationError):
    pass


class ForbiddenError(UserError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message, status_code=403)


class InvalidEmailDomainError(UserError):
    def __init__(self) -> None:
        super().__init__(
            "This Google account is not associated with NIT Raipur.",
            status_code=403,
        )


class AccountInactiveError(UserError):
    def __init__(
        self,
        message: str = (
            "Your account is currently inactive. Please contact the Placement Cell."
        ),
    ) -> None:
        super().__init__(message, status_code=403)
