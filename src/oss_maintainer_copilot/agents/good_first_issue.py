from __future__ import annotations

from oss_maintainer_copilot.agents.issue_triage import IssueTriageAgent
from oss_maintainer_copilot.schemas.common import DifficultyLevel, IssueCategory
from oss_maintainer_copilot.schemas.good_first_issue import GoodFirstIssueResult
from oss_maintainer_copilot.schemas.triage import IssueTriageInput, IssueTriageResult


class GoodFirstIssueAgent:
    """Dedicated good-first-issue classifier built on top of issue triage signals."""

    def classify(
        self,
        issue: IssueTriageInput,
        triage_result: IssueTriageResult | None = None,
    ) -> GoodFirstIssueResult:
        triage = triage_result or IssueTriageAgent().triage(issue)

        matched_signals: list[str] = []
        blocked_by: list[str] = []

        if triage.category in {IssueCategory.DOCS, IssueCategory.BUG}:
            matched_signals.append(f"category:{triage.category.value}")
        else:
            blocked_by.append(f"category:{triage.category.value}")

        if triage.difficulty is DifficultyLevel.BEGINNER:
            matched_signals.append("difficulty:beginner")
        else:
            blocked_by.append(f"difficulty:{triage.difficulty.value}")

        if not triage.missing_context:
            matched_signals.append("well-specified")
        else:
            blocked_by.extend(f"missing:{item}" for item in triage.missing_context)

        if triage.good_first_issue:
            matched_signals.append("triage-approved")
        else:
            blocked_by.append("triage-not-approved")

        eligible = triage.good_first_issue and not triage.missing_context
        confidence = round(min(max(triage.confidence + (0.08 if eligible else -0.06), 0.0), 0.99), 2)

        reasoning = [
            f"Category {triage.category.value} is {'friendly' if triage.category in {IssueCategory.DOCS, IssueCategory.BUG} else 'not ideal'} for onboarding.",
            f"Difficulty was classified as {triage.difficulty.value}.",
            "Issue has enough context for a newcomer." if not triage.missing_context else "Issue is missing context needed for a safe handoff.",
            "The issue is suitable as a good first issue." if eligible else "The issue should not be marked as a good first issue yet.",
        ]

        return GoodFirstIssueResult(
            eligible=eligible,
            confidence=confidence,
            matched_signals=matched_signals,
            blocked_by=blocked_by,
            reasoning=reasoning,
        )
