import enum


class EligibilityReasonCode(str, enum.Enum):
    PROFILE_MISSING = "PROFILE_MISSING"
    ACADEMIC_INFO_MISSING = "ACADEMIC_INFO_MISSING"
    PERSONAL_INFO_MISSING = "PERSONAL_INFO_MISSING"
    CGPA_BELOW_MINIMUM = "CGPA_BELOW_MINIMUM"
    DEPARTMENT_NOT_ALLOWED = "DEPARTMENT_NOT_ALLOWED"
    GRADUATION_YEAR_NOT_ALLOWED = "GRADUATION_YEAR_NOT_ALLOWED"
    ACTIVE_BACKLOGS_EXCEEDED = "ACTIVE_BACKLOGS_EXCEEDED"
    BACKLOG_HISTORY_NOT_ALLOWED = "BACKLOG_HISTORY_NOT_ALLOWED"
    GENDER_RESTRICTED = "GENDER_RESTRICTED"
    EDUCATION_TYPE_MISSING = "EDUCATION_TYPE_MISSING"
    EDUCATION_SCORE_BELOW_MINIMUM = "EDUCATION_SCORE_BELOW_MINIMUM"


REASON_TITLES: dict[EligibilityReasonCode, str] = {
    EligibilityReasonCode.PROFILE_MISSING: "Student Profile",
    EligibilityReasonCode.ACADEMIC_INFO_MISSING: "Academic Information",
    EligibilityReasonCode.PERSONAL_INFO_MISSING: "Personal Information",
    EligibilityReasonCode.CGPA_BELOW_MINIMUM: "CGPA",
    EligibilityReasonCode.DEPARTMENT_NOT_ALLOWED: "Department",
    EligibilityReasonCode.GRADUATION_YEAR_NOT_ALLOWED: "Graduation Year",
    EligibilityReasonCode.ACTIVE_BACKLOGS_EXCEEDED: "Backlogs",
    EligibilityReasonCode.BACKLOG_HISTORY_NOT_ALLOWED: "Backlog History",
    EligibilityReasonCode.GENDER_RESTRICTED: "Gender",
    EligibilityReasonCode.EDUCATION_TYPE_MISSING: "Education Requirements",
    EligibilityReasonCode.EDUCATION_SCORE_BELOW_MINIMUM: "Education Requirements",
}

# Deterministic education_requirements keys → EducationType value
EDUCATION_MIN_SCORE_KEYS: dict[str, str] = {
    "minimum_secondary_percentage": "SECONDARY",
    "minimum_higher_secondary_percentage": "HIGHER_SECONDARY",
    "minimum_diploma_percentage": "DIPLOMA",
    "minimum_undergraduate_percentage": "UNDERGRADUATE",
}
