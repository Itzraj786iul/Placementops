from app.platform.exceptions import ApplicationError


class HiringOpportunityError(ApplicationError):
    pass


class OpportunityNotFoundError(HiringOpportunityError):
    def __init__(self, message: str = "Hiring opportunity not found") -> None:
        super().__init__(message, status_code=404)


class OpportunityForbiddenError(HiringOpportunityError):
    def __init__(self, message: str = "You do not have access to this opportunity") -> None:
        super().__init__(message, status_code=403)


class OpportunityValidationError(HiringOpportunityError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=422)


class OpportunityConflictError(HiringOpportunityError):
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=409)
