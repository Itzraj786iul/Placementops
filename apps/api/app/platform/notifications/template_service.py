from __future__ import annotations

from dataclasses import dataclass
from string import Template

from app.platform.notifications.enums import NotificationType


@dataclass(frozen=True)
class RenderedTemplate:
    subject: str
    title: str
    message: str
    html: str
    text: str


_TEMPLATES: dict[NotificationType, dict[str, str]] = {
    NotificationType.OPPORTUNITY_PUBLISHED: {
        "subject": "New hiring opportunity: $opportunity_title",
        "title": "New hiring opportunity published",
        "message": (
            "$opportunity_title is now open for applications"
            "$deadline_clause. Review eligibility and apply in PlacementOS."
        ),
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>New hiring opportunity</h2>
  <p><strong>$opportunity_title</strong> has been published.</p>
  <p>$deadline_line</p>
  <p><a href="$action_url">View opportunity</a></p>
  <p style="color:#666;font-size:12px">PlacementOS · NIT Raipur</p>
</body></html>
""".strip(),
        "text": (
            "New hiring opportunity: $opportunity_title\n"
            "$deadline_line\n"
            "View: $action_url\n"
        ),
    },
    NotificationType.APPLICATION_SUBMITTED: {
        "subject": "Application submitted: $opportunity_title",
        "title": "Application submitted",
        "message": "Your application for $opportunity_title was submitted successfully.",
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Application submitted</h2>
  <p>Your application for <strong>$opportunity_title</strong> was submitted successfully.</p>
  <p><a href="$action_url">View application</a></p>
</body></html>
""".strip(),
        "text": "Application submitted for $opportunity_title.\nView: $action_url\n",
    },
    NotificationType.APPLICATION_WITHDRAWN: {
        "subject": "Application withdrawn: $opportunity_title",
        "title": "Application withdrawn",
        "message": "Your application for $opportunity_title has been withdrawn.",
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Application withdrawn</h2>
  <p>Your application for <strong>$opportunity_title</strong> has been withdrawn.</p>
  <p><a href="$action_url">Open PlacementOS</a></p>
</body></html>
""".strip(),
        "text": "Application withdrawn for $opportunity_title.\n",
    },
    NotificationType.APPLICATION_STATUS_CHANGED: {
        "subject": "Application update: $opportunity_title",
        "title": "Application status updated",
        "message": (
            "Your application for $opportunity_title changed from "
            "$old_status to $new_status."
        ),
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Application status updated</h2>
  <p>Your application for <strong>$opportunity_title</strong> changed from
  <strong>$old_status</strong> to <strong>$new_status</strong>.</p>
  <p><a href="$action_url">View application</a></p>
</body></html>
""".strip(),
        "text": (
            "Application for $opportunity_title: $old_status → $new_status\n"
            "View: $action_url\n"
        ),
    },
    NotificationType.SHORTLISTED: {
        "subject": "Shortlisted: $opportunity_title",
        "title": "You have been shortlisted",
        "message": "Congratulations — you are shortlisted for $opportunity_title.",
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Shortlisted</h2>
  <p>Congratulations — you have been shortlisted for
  <strong>$opportunity_title</strong>.</p>
  <p><a href="$action_url">View details</a></p>
</body></html>
""".strip(),
        "text": "You are shortlisted for $opportunity_title.\nView: $action_url\n",
    },
    NotificationType.INTERVIEW_SCHEDULED: {
        "subject": "Interview scheduled: $opportunity_title",
        "title": "Interview scheduled",
        "message": (
            "An interview has been scheduled for $opportunity_title"
            "$interview_when."
        ),
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Interview scheduled</h2>
  <p>An interview has been scheduled for <strong>$opportunity_title</strong>.</p>
  <p>$interview_details</p>
  <p><a href="$action_url">View details</a></p>
</body></html>
""".strip(),
        "text": (
            "Interview scheduled for $opportunity_title.\n"
            "$interview_details\n"
            "View: $action_url\n"
        ),
    },
    NotificationType.OFFER_RELEASED: {
        "subject": "Offer released: $opportunity_title",
        "title": "Offer released",
        "message": "An offer has been released for $opportunity_title. Check PlacementOS for next steps.",
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Offer released</h2>
  <p>An offer has been released for <strong>$opportunity_title</strong>.</p>
  <p>Please review next steps in PlacementOS.</p>
  <p><a href="$action_url">View offer</a></p>
</body></html>
""".strip(),
        "text": "Offer released for $opportunity_title.\nView: $action_url\n",
    },
    NotificationType.PROFILE_SUBMITTED: {
        "subject": "Student profile submitted: $student_name",
        "title": "Student profile submitted for review",
        "message": (
            "$student_name ($roll_number) submitted their placement profile "
            "for review."
        ),
        "html": """
<html><body style="font-family:system-ui,sans-serif;line-height:1.5;color:#111">
  <h2>Student profile submitted</h2>
  <p><strong>$student_name</strong> ($roll_number) submitted their placement
  profile for review.</p>
  <p><a href="$action_url">Open student workspace</a></p>
</body></html>
""".strip(),
        "text": (
            "Student profile submitted: $student_name ($roll_number)\n"
            "Open: $action_url\n"
        ),
    },
}


class TemplateService:
    """Render reusable notification / email templates."""

    def render(
        self,
        notification_type: NotificationType,
        context: dict[str, str],
    ) -> RenderedTemplate:
        raw = _TEMPLATES.get(notification_type)
        if raw is None:
            raise KeyError(f"No template for {notification_type}")

        safe = {k: str(v) for k, v in context.items()}
        # Provide empty defaults for optional placeholders
        for key in (
            "opportunity_title",
            "action_url",
            "deadline_clause",
            "deadline_line",
            "old_status",
            "new_status",
            "interview_when",
            "interview_details",
            "student_name",
            "roll_number",
        ):
            safe.setdefault(key, "")

        def sub(value: str) -> str:
            return Template(value).safe_substitute(safe)

        return RenderedTemplate(
            subject=sub(raw["subject"]),
            title=sub(raw["title"]),
            message=sub(raw["message"]),
            html=sub(raw["html"]),
            text=sub(raw["text"]),
        )

    def available_templates(self) -> list[NotificationType]:
        return list(_TEMPLATES.keys())
