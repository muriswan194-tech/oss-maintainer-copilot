from __future__ import annotations

from dataclasses import dataclass

from oss_maintainer_copilot.schemas.common import IssueCategory
from oss_maintainer_copilot.schemas.triage import IssueTriageInput, RepositoryMetadata

BUG_KEYWORDS = {
    "bug",
    "crash",
    "error",
    "fail",
    "failing",
    "incorrect",
    "regression",
    "traceback",
}
DOCS_KEYWORDS = {
    "docs",
    "documentation",
    "guide",
    "readme",
    "tutorial",
    "typo",
}
FEATURE_KEYWORDS = {
    "allow",
    "enhancement",
    "feature",
    "new",
    "request",
    "support",
}
REFACTOR_KEYWORDS = {
    "cleanup",
    "extract",
    "refactor",
    "reorganize",
    "rename",
    "simplify",
    "technical debt",
}
HIGH_RISK_KEYWORDS = {
    "architecture",
    "authentication",
    "backward compatibility",
    "breaking",
    "compliance",
    "database",
    "migration",
    "performance",
    "release process",
    "security",
}
SURFACE_AREA_HINTS = {
    "api",
    "cli",
    "database",
    "docs",
    "documentation",
    "frontend",
    "workflow",
}
REPRODUCTION_HINTS = {
    "reproduce",
    "steps to reproduce",
    "actual behavior",
    "expected behavior",
}
ACCEPTANCE_HINTS = {"acceptance criteria", "done when", "success criteria"}
TARGET_HINTS = {"file", "module", "component", "readme", "workflow", "tests", "docs"}


@dataclass(frozen=True)
class IssueSignals:
    category_scores: dict[IssueCategory, int]
    high_risk_hits: set[str]
    surface_area_hits: set[str]
    body_word_count: int
    labels: set[str]
    has_reproduction: bool
    has_expected_behavior: bool
    has_acceptance_criteria: bool
    has_target_area: bool
    empty_body: bool


class IssueSignalCollector:
    """Collect deterministic triage signals from an issue payload."""

    def collect(self, issue: IssueTriageInput) -> IssueSignals:
        text = self._normalize(issue.title, issue.body, issue.labels, issue.repository)
        labels = {label.casefold() for label in issue.labels}
        category_scores = {
            IssueCategory.BUG: self._keyword_score(
                text,
                labels,
                BUG_KEYWORDS,
                {"bug", "type: bug"},
            ),
            IssueCategory.DOCS: self._keyword_score(
                text,
                labels,
                DOCS_KEYWORDS,
                {"docs", "documentation"},
            ),
            IssueCategory.FEATURE_REQUEST: self._keyword_score(
                text,
                labels,
                FEATURE_KEYWORDS,
                {"enhancement", "feature", "type: feature"},
            ),
            IssueCategory.REFACTOR: self._keyword_score(
                text,
                labels,
                REFACTOR_KEYWORDS,
                {"refactor", "cleanup", "technical debt"},
            ),
            IssueCategory.AMBIGUOUS: 0,
        }

        return IssueSignals(
            category_scores=category_scores,
            high_risk_hits={
                keyword for keyword in HIGH_RISK_KEYWORDS if keyword in text
            },
            surface_area_hits={
                keyword for keyword in SURFACE_AREA_HINTS if keyword in text
            },
            body_word_count=len(issue.body.split()),
            labels=labels,
            has_reproduction=any(hint in text for hint in REPRODUCTION_HINTS),
            has_expected_behavior=(
                "expected behavior" in text or "expected" in text
            ),
            has_acceptance_criteria=any(
                hint in text for hint in ACCEPTANCE_HINTS
            ),
            has_target_area=any(hint in text for hint in TARGET_HINTS),
            empty_body=issue.body.strip() == "",
        )

    def _normalize(
        self,
        title: str,
        body: str,
        labels: list[str],
        repository: RepositoryMetadata | None,
    ) -> str:
        repo_text = ""
        if repository is not None:
            repo_text = " ".join(
                value
                for value in [
                    repository.full_name or "",
                    repository.primary_language or "",
                    *repository.topics,
                ]
                if value
            )
        return " ".join([title, body, " ".join(labels), repo_text]).casefold()

    def _keyword_score(
        self,
        text: str,
        labels: set[str],
        keywords: set[str],
        label_matches: set[str],
    ) -> int:
        keyword_hits = sum(1 for keyword in keywords if keyword in text)
        label_hits = sum(2 for label in label_matches if label in labels)
        return keyword_hits + label_hits
