import enum


class ProfileStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class DocumentStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class EducationType(str, enum.Enum):
    SECONDARY = "SECONDARY"
    HIGHER_SECONDARY = "HIGHER_SECONDARY"
    DIPLOMA = "DIPLOMA"
    UNDERGRADUATE = "UNDERGRADUATE"


class Gender(str, enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class DocumentType(str, enum.Enum):
    PHOTO = "PHOTO"
    AADHAR = "AADHAR"
    PAN = "PAN"
    TENTH_MARKSHEET = "TENTH_MARKSHEET"
    TWELFTH_MARKSHEET = "TWELFTH_MARKSHEET"
    SEMESTER_MARKSHEET = "SEMESTER_MARKSHEET"
    RESUME = "RESUME"
    OTHER = "OTHER"


class VerificationStatus(str, enum.Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"
