import enum

from app.modules.applications.enums import ApplicationStatus


class MatchField(str, enum.Enum):
    ROLL_NUMBER = "ROLL_NUMBER"
    REGISTRATION_NUMBER = "REGISTRATION_NUMBER"
    EMAIL = "EMAIL"


class ImportStatus(str, enum.Enum):
    PREVIEW = "PREVIEW"
    CONFIRMED = "CONFIRMED"


class RowMatchStatus(str, enum.Enum):
    MATCHED = "MATCHED"
    UNMATCHED = "UNMATCHED"
    DUPLICATE = "DUPLICATE"
    INVALID = "INVALID"


IMPORTABLE_STATUSES: set[ApplicationStatus] = {
    ApplicationStatus.SHORTLISTED,
    ApplicationStatus.ASSESSMENT,
    ApplicationStatus.INTERVIEW,
    ApplicationStatus.SELECTED,
    ApplicationStatus.OFFER_RELEASED,
    ApplicationStatus.REJECTED,
}

# Common header aliases → normalized match field usage
HEADER_ALIASES: dict[MatchField, set[str]] = {
    MatchField.ROLL_NUMBER: {
        "roll",
        "roll number",
        "roll_number",
        "roll no",
        "rollno",
        "roll no.",
    },
    MatchField.REGISTRATION_NUMBER: {
        "registration",
        "registration number",
        "registration_number",
        "reg number",
        "reg_number",
        "reg no",
        "regno",
    },
    MatchField.EMAIL: {
        "email",
        "e-mail",
        "college email",
        "college_email",
        "personal email",
        "personal_email",
        "student email",
    },
}
