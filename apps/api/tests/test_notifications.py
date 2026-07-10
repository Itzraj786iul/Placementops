from app.platform.notifications.enums import NotificationType
from app.platform.notifications.template_service import TemplateService


def test_all_initial_templates_exist() -> None:
    service = TemplateService()
    expected = {
        NotificationType.OPPORTUNITY_PUBLISHED,
        NotificationType.APPLICATION_SUBMITTED,
        NotificationType.APPLICATION_WITHDRAWN,
        NotificationType.APPLICATION_STATUS_CHANGED,
        NotificationType.SHORTLISTED,
        NotificationType.INTERVIEW_SCHEDULED,
        NotificationType.OFFER_RELEASED,
    }
    assert set(service.available_templates()) == expected


def test_render_opportunity_published() -> None:
    rendered = TemplateService().render(
        NotificationType.OPPORTUNITY_PUBLISHED,
        {
            "opportunity_title": "Acme SDE",
            "action_url": "https://example.com/opportunities/1",
            "deadline_line": "Application deadline: 01 Aug 2026.",
            "deadline_clause": " (deadline 01 Aug 2026)",
        },
    )
    assert "Acme SDE" in rendered.subject
    assert "Acme SDE" in rendered.message
    assert "https://example.com/opportunities/1" in rendered.html
    assert rendered.title == "New hiring opportunity published"


def test_render_shortlisted() -> None:
    rendered = TemplateService().render(
        NotificationType.SHORTLISTED,
        {
            "opportunity_title": "Beta Intern",
            "action_url": "https://example.com/applications",
        },
    )
    assert "shortlisted" in rendered.message.lower()
    assert "Beta Intern" in rendered.html


def test_email_provider_null_when_unconfigured() -> None:
    from app.platform.notifications.email_provider import NullEmailProvider
    from app.platform.notifications.email_provider import EmailMessage

    result = NullEmailProvider().send(
        EmailMessage(
            to="student@nitrr.ac.in",
            subject="Test",
            html="<p>Hi</p>",
            text="Hi",
        ),
    )
    assert result.success is False
    assert result.error is not None
