import enum


class EmploymentType(str, enum.Enum):
    INTERNSHIP = "INTERNSHIP"
    FULL_TIME = "FULL_TIME"
    PPO = "PPO"
    INTERNSHIP_PPO = "INTERNSHIP_PPO"


class WorkMode(str, enum.Enum):
    ONSITE = "ONSITE"
    HYBRID = "HYBRID"
    REMOTE = "REMOTE"


class OpportunityStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class OpportunityDocumentType(str, enum.Enum):
    JD = "JD"
    ELIGIBILITY = "ELIGIBILITY"
    PPT = "PPT"
    OTHER = "OTHER"


class TimelineStage(str, enum.Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    APPLICATIONS_OPEN = "APPLICATIONS_OPEN"
    APPLICATIONS_CLOSED = "APPLICATIONS_CLOSED"
    SHORTLIST_RELEASED = "SHORTLIST_RELEASED"
    ASSESSMENT = "ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    SELECTED = "SELECTED"
    OFFER_RELEASED = "OFFER_RELEASED"
    COMPLETED = "COMPLETED"
