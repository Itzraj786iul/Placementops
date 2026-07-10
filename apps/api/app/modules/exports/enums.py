import enum


class ExportFormat(str, enum.Enum):
    CSV = "csv"
    XLSX = "xlsx"


class ExportScope(str, enum.Enum):
    ALL = "all"
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"


class ExportColumn(str, enum.Enum):
    ROLL_NUMBER = "roll_number"
    REGISTRATION_NUMBER = "registration_number"
    STUDENT_NAME = "student_name"
    DEPARTMENT = "department"
    DEPARTMENT_CODE = "department_code"
    CGPA = "cgpa"
    ACTIVE_BACKLOGS = "active_backlogs"
    HISTORY_BACKLOGS = "history_backlogs"
    GRADUATION_YEAR = "graduation_year"
    GENDER = "gender"
    PERSONAL_EMAIL = "personal_email"
    PHONE_NUMBER = "phone_number"
    RESUME_USED = "resume_used"
    APPLICATION_STATUS = "application_status"
    APPLIED_AT = "applied_at"
    ELIGIBILITY = "eligibility"
    COMPANY = "company"


COLUMN_LABELS: dict[ExportColumn, str] = {
    ExportColumn.ROLL_NUMBER: "Roll Number",
    ExportColumn.REGISTRATION_NUMBER: "Registration Number",
    ExportColumn.STUDENT_NAME: "Student Name",
    ExportColumn.DEPARTMENT: "Department",
    ExportColumn.DEPARTMENT_CODE: "Department Code",
    ExportColumn.CGPA: "CGPA",
    ExportColumn.ACTIVE_BACKLOGS: "Active Backlogs",
    ExportColumn.HISTORY_BACKLOGS: "History Backlogs",
    ExportColumn.GRADUATION_YEAR: "Graduation Year",
    ExportColumn.GENDER: "Gender",
    ExportColumn.PERSONAL_EMAIL: "Personal Email",
    ExportColumn.PHONE_NUMBER: "Phone Number",
    ExportColumn.RESUME_USED: "Resume Used",
    ExportColumn.APPLICATION_STATUS: "Application Status",
    ExportColumn.APPLIED_AT: "Applied At",
    ExportColumn.ELIGIBILITY: "Eligibility",
    ExportColumn.COMPANY: "Company",
}

DEFAULT_COLUMNS: list[ExportColumn] = [
    ExportColumn.ROLL_NUMBER,
    ExportColumn.REGISTRATION_NUMBER,
    ExportColumn.STUDENT_NAME,
    ExportColumn.DEPARTMENT,
    ExportColumn.CGPA,
    ExportColumn.ACTIVE_BACKLOGS,
    ExportColumn.HISTORY_BACKLOGS,
    ExportColumn.GRADUATION_YEAR,
    ExportColumn.RESUME_USED,
    ExportColumn.APPLICATION_STATUS,
    ExportColumn.APPLIED_AT,
]
