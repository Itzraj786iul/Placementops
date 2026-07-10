import enum


class CompanyStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class OwnershipType(str, enum.Enum):
    LEGACY = "LEGACY"
    NEW = "NEW"
    TRANSFERRED = "TRANSFERRED"


class PipelineStage(str, enum.Enum):
    NOT_CONTACTED = "NOT_CONTACTED"
    INVITATION_SENT = "INVITATION_SENT"
    FOLLOW_UP_PENDING = "FOLLOW_UP_PENDING"
    HR_REPLIED = "HR_REPLIED"
    MEETING_SCHEDULED = "MEETING_SCHEDULED"
    INTERESTED = "INTERESTED"
    ON_HOLD = "ON_HOLD"
    REJECTED = "REJECTED"
    DRIVE_PLANNED = "DRIVE_PLANNED"


class CommunicationType(str, enum.Enum):
    EMAIL = "EMAIL"
    CALL = "CALL"
    MEETING = "MEETING"
    WHATSAPP = "WHATSAPP"
    OTHER = "OTHER"


class CompanyDocumentType(str, enum.Enum):
    JD = "JD"
    ELIGIBILITY = "ELIGIBILITY"
    PPT = "PPT"
    OFFER_TEMPLATE = "OFFER_TEMPLATE"
    BOND = "BOND"
    OTHER = "OTHER"
