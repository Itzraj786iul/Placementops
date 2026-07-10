from __future__ import annotations

import uuid
from collections import Counter

from app.modules.eligibility.enums import EligibilityReasonCode
from app.modules.eligibility.schemas import (
    EligibilityReason,
    ReasonBreakdownItem,
    ScreeningSummaryResponse,
)


def aggregate_screening(
    opportunity_id: uuid.UUID,
    evaluations: list[list[EligibilityReason]],
) -> ScreeningSummaryResponse:
    """Pure aggregation helper for screening summaries (testable without DB)."""
    eligible_count = 0
    ineligible_count = 0
    reason_counter: Counter[EligibilityReasonCode] = Counter()
    reason_titles: dict[EligibilityReasonCode, str] = {}

    for reasons in evaluations:
        if not reasons:
            eligible_count += 1
            continue

        ineligible_count += 1
        seen: set[EligibilityReasonCode] = set()
        for reason in reasons:
            if reason.code in seen:
                continue
            seen.add(reason.code)
            reason_counter[reason.code] += 1
            reason_titles[reason.code] = reason.title

    return ScreeningSummaryResponse(
        hiring_opportunity_id=opportunity_id,
        total_applications=len(evaluations),
        eligible_count=eligible_count,
        ineligible_count=ineligible_count,
        reason_breakdown=[
            ReasonBreakdownItem(
                code=code,
                title=reason_titles[code],
                count=count,
            )
            for code, count in reason_counter.most_common()
        ],
    )
