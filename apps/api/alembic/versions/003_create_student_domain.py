"""Create student domain tables and seed departments

Revision ID: 003_student_domain
Revises: 002_user_domain
Create Date: 2026-07-09

"""

import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_student_domain"
down_revision: str | None = "002_user_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEPARTMENTS = [
    ("Computer Science and Engineering", "CSE"),
    ("Information Technology", "IT"),
    ("Electronics and Communication Engineering", "ECE"),
    ("Electrical Engineering", "EE"),
    ("Mechanical Engineering", "ME"),
    ("Civil Engineering", "CE"),
    ("Chemical Engineering", "CH"),
    ("Metallurgical and Materials Engineering", "MME"),
    ("Mining Engineering", "MN"),
    ("Biotechnology", "BT"),
]

profile_status_enum = postgresql.ENUM(
    "DRAFT",
    "SUBMITTED",
    "UNDER_REVIEW",
    "VERIFIED",
    "REJECTED",
    name="profile_status_enum",
    create_type=False,
)
gender_enum = postgresql.ENUM(
    "MALE", "FEMALE", "OTHER", name="gender_enum", create_type=False
)
education_type_enum = postgresql.ENUM(
    "SECONDARY",
    "HIGHER_SECONDARY",
    "DIPLOMA",
    "UNDERGRADUATE",
    name="education_type_enum",
    create_type=False,
)
document_type_enum = postgresql.ENUM(
    "PHOTO",
    "AADHAR",
    "PAN",
    "TENTH_MARKSHEET",
    "TWELFTH_MARKSHEET",
    "SEMESTER_MARKSHEET",
    "RESUME",
    "OTHER",
    name="document_type_enum",
    create_type=False,
)
document_status_enum = postgresql.ENUM(
    "PENDING",
    "VERIFIED",
    "REJECTED",
    name="document_status_enum",
    create_type=False,
)
verification_status_enum = postgresql.ENUM(
    "PENDING",
    "VERIFIED",
    "REJECTED",
    name="verification_status_enum",
    create_type=False,
)


def upgrade() -> None:
    profile_status_enum.create(op.get_bind(), checkfirst=True)
    gender_enum.create(op.get_bind(), checkfirst=True)
    education_type_enum.create(op.get_bind(), checkfirst=True)
    document_type_enum.create(op.get_bind(), checkfirst=True)
    document_status_enum.create(op.get_bind(), checkfirst=True)
    verification_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "departments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_departments_code", "departments", ["code"])

    op.create_table(
        "student_profiles",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("department_id", sa.Uuid(), nullable=False),
        sa.Column("roll_number", sa.String(length=50), nullable=False),
        sa.Column("registration_number", sa.String(length=50), nullable=False),
        sa.Column("graduation_year", sa.Integer(), nullable=False),
        sa.Column(
            "profile_status",
            profile_status_enum,
            nullable=False,
            server_default="DRAFT",
        ),
        sa.Column("profile_completion", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("registration_number"),
        sa.UniqueConstraint("roll_number"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])
    op.create_index("ix_student_profiles_department_id", "student_profiles", ["department_id"])
    op.create_index("ix_student_profiles_roll_number", "student_profiles", ["roll_number"])

    op.create_table(
        "student_personal_information",
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("gender", gender_enum, nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=False),
        sa.Column("phone_number", sa.String(length=20), nullable=False),
        sa.Column("alternate_phone", sa.String(length=20), nullable=True),
        sa.Column("personal_email", sa.String(length=255), nullable=True),
        sa.Column("address", sa.Text(), nullable=False),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("country", sa.String(length=100), nullable=False),
        sa.Column("photo_url", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_profile_id"),
    )

    op.create_table(
        "student_academic_information",
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("current_cgpa", sa.Numeric(4, 2), nullable=False),
        sa.Column("active_backlogs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_history_backlogs", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("semester", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_profile_id"),
    )

    op.create_table(
        "student_education_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("education_type", education_type_enum, nullable=False),
        sa.Column("institution", sa.String(length=255), nullable=False),
        sa.Column("board", sa.String(length=255), nullable=False),
        sa.Column("passing_year", sa.Integer(), nullable=False),
        sa.Column("percentage_or_cgpa", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_student_education_history_student_profile_id",
        "student_education_history",
        ["student_profile_id"],
    )

    op.create_table(
        "student_resume_library",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("last_used", sa.DateTime(timezone=True), nullable=True),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_student_resume_library_student_profile_id",
        "student_resume_library",
        ["student_profile_id"],
    )

    op.create_table(
        "student_documents",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("document_type", document_type_enum, nullable=False),
        sa.Column("file_url", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column(
            "status",
            document_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_student_documents_student_profile_id",
        "student_documents",
        ["student_profile_id"],
    )

    op.create_table(
        "student_skills",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("skill_name", sa.String(length=100), nullable=False),
        sa.Column("skill_level", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_student_skills_student_profile_id",
        "student_skills",
        ["student_profile_id"],
    )

    op.create_table(
        "student_projects",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("tech_stack", sa.String(length=500), nullable=False),
        sa.Column("github_url", sa.String(length=500), nullable=True),
        sa.Column("demo_url", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_student_projects_student_profile_id",
        "student_projects",
        ["student_profile_id"],
    )

    op.create_table(
        "student_verification",
        sa.Column("student_profile_id", sa.Uuid(), nullable=False),
        sa.Column(
            "personal_status",
            verification_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "academic_status",
            verification_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "documents_status",
            verification_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "resume_status",
            verification_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column(
            "overall_status",
            verification_status_enum,
            nullable=False,
            server_default="PENDING",
        ),
        sa.Column("reviewer_id", sa.Uuid(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["reviewer_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("student_profile_id"),
    )

    departments_table = sa.table(
        "departments",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("code", sa.String()),
        sa.column("created_at", sa.DateTime(timezone=True)),
    )
    now = datetime.now(timezone.utc)
    op.bulk_insert(
        departments_table,
        [
            {
                "id": uuid.uuid4(),
                "name": name,
                "code": code,
                "created_at": now,
            }
            for name, code in DEPARTMENTS
        ],
    )


def downgrade() -> None:
    op.drop_table("student_verification")
    op.drop_table("student_projects")
    op.drop_table("student_skills")
    op.drop_table("student_documents")
    op.drop_table("student_resume_library")
    op.drop_table("student_education_history")
    op.drop_table("student_academic_information")
    op.drop_table("student_personal_information")
    op.drop_table("student_profiles")
    op.drop_table("departments")

    verification_status_enum.drop(op.get_bind(), checkfirst=True)
    document_status_enum.drop(op.get_bind(), checkfirst=True)
    document_type_enum.drop(op.get_bind(), checkfirst=True)
    education_type_enum.drop(op.get_bind(), checkfirst=True)
    gender_enum.drop(op.get_bind(), checkfirst=True)
    profile_status_enum.drop(op.get_bind(), checkfirst=True)
