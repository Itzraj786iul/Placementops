from app.modules.hiring_opportunities.enums import OpportunityStatus, TimelineStage

# Valid hiring_opportunity.status transitions (staff actions)
STATUS_TRANSITIONS: dict[OpportunityStatus, set[OpportunityStatus]] = {
    OpportunityStatus.DRAFT: {OpportunityStatus.PUBLISHED, OpportunityStatus.ARCHIVED},
    OpportunityStatus.PUBLISHED: {OpportunityStatus.ARCHIVED},
    OpportunityStatus.ARCHIVED: set(),
}

# Ordered timeline stages for forward-only validation
TIMELINE_STAGE_ORDER: list[TimelineStage] = [
    TimelineStage.DRAFT,
    TimelineStage.PUBLISHED,
    TimelineStage.APPLICATIONS_OPEN,
    TimelineStage.APPLICATIONS_CLOSED,
    TimelineStage.SHORTLIST_RELEASED,
    TimelineStage.ASSESSMENT,
    TimelineStage.INTERVIEW,
    TimelineStage.SELECTED,
    TimelineStage.OFFER_RELEASED,
    TimelineStage.COMPLETED,
]


def validate_status_transition(
    current: OpportunityStatus,
    target: OpportunityStatus,
) -> None:
    allowed = STATUS_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValueError(
            f"Cannot transition opportunity status from {current.value} to {target.value}",
        )


def validate_timeline_transition(
    current: TimelineStage | None,
    target: TimelineStage,
) -> None:
    if current is None:
        if target != TimelineStage.DRAFT:
            raise ValueError("Initial timeline stage must be DRAFT")
        return

    current_index = TIMELINE_STAGE_ORDER.index(current)
    target_index = TIMELINE_STAGE_ORDER.index(target)
    if target_index < current_index:
        raise ValueError(
            f"Cannot move timeline backward from {current.value} to {target.value}",
        )
