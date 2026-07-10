#!/usr/bin/env python3
"""Seed development users with email/password login for each role."""

from __future__ import annotations

import sys
from pathlib import Path

API_DIR = Path(__file__).resolve().parents[1] / "apps" / "api"
sys.path.insert(0, str(API_DIR))

from app.core.config import settings  # noqa: E402
from app.database.session import SessionLocal  # noqa: E402
from app.modules.users.repository import UserRepository  # noqa: E402
from app.modules.users.schemas import CreateUserData  # noqa: E402
from app.platform.auth.password import hash_password  # noqa: E402

DEFAULT_DEV_PASSWORD = "PlacementOS123!"

DEV_USERS: list[tuple[str, str, str, str]] = [
    ("admin@nitrr.ac.in", "Super", "Admin", "SUPER_ADMIN"),
    ("cell@nitrr.ac.in", "Placement", "Cell", "PLACEMENT_CELL"),
    ("convener@nitrr.ac.in", "Placement", "Convener", "PLACEMENT_CONVENER"),
    ("student@nitrr.ac.in", "Demo", "Student", "STUDENT"),
]


def seed_dev_users() -> None:
    db = SessionLocal()
    repository = UserRepository(db)

    try:
        repository.seed_roles()
        password_hash = hash_password(DEFAULT_DEV_PASSWORD)

        for email, first_name, last_name, role_name in DEV_USERS:
            user = repository.get_by_college_email(email)
            if user is None:
                user = repository.create_user(
                    CreateUserData(
                        college_email=email,
                        first_name=first_name,
                        last_name=last_name,
                        display_name=f"{first_name} {last_name}",
                        email_verified=True,
                    ),
                )
                db.flush()

            repository.clear_roles(user.id)
            role = repository.get_role_by_name(role_name)
            if role is None:
                raise RuntimeError(f"Role not found: {role_name}")
            repository.assign_role(user.id, role.id)
            repository.set_password_hash(user, password_hash)

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    if not settings.ENABLE_DEV_LOGIN:
        print(
            "WARNING: ENABLE_DEV_LOGIN is false. "
            "Set ENABLE_DEV_LOGIN=true in apps/api/.env before using dev login.",
        )

    seed_dev_users()

    print("")
    print("Development users seeded successfully.")
    print("")
    print("Use these credentials on http://localhost:3000/login")
    print("(Dev login section appears when NEXT_PUBLIC_ENABLE_DEV_LOGIN=true)")
    print("")
    print(f"Password for all accounts: {DEFAULT_DEV_PASSWORD}")
    print("")
    for email, first_name, last_name, role_name in DEV_USERS:
        print(f"  {role_name:20}  {email}")
    print("")


if __name__ == "__main__":
    main()
