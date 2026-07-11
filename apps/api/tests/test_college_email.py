from app.core.config import settings
from app.modules.users.exceptions import InvalidEmailDomainError
from app.modules.users.service import UserService


class _DummyDb:
    pass


def test_accepts_root_college_domain() -> None:
    service = UserService(_DummyDb())  # type: ignore[arg-type]
    assert (
        service.validate_college_email("student@nitrr.ac.in")
        == "student@nitrr.ac.in"
    )


def test_accepts_department_subdomain() -> None:
    service = UserService(_DummyDb())  # type: ignore[arg-type]
    assert (
        service.validate_college_email("ransari078.btech2023@mme.nitrr.ac.in")
        == "ransari078.btech2023@mme.nitrr.ac.in"
    )


def test_rejects_non_college_domain() -> None:
    service = UserService(_DummyDb())  # type: ignore[arg-type]
    try:
        service.validate_college_email("user@gmail.com")
        raise AssertionError("expected InvalidEmailDomainError")
    except InvalidEmailDomainError:
        pass


def test_allowed_domain_setting_is_nitrr() -> None:
    assert settings.ALLOWED_EMAIL_DOMAIN.endswith("nitrr.ac.in")
