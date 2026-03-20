from __future__ import annotations

from oss_maintainer_copilot.agents.triage_rendering import (
    build_triage_labels,
    render_triage_markdown,
)
from oss_maintainer_copilot.agents.triage_scoring import IssueTriageScorer
from oss_maintainer_copilot.agents.triage_signals import IssueSignalCollector
from oss_maintainer_copilot.schemas.github import GitHubIssue, GitHubRepository
from oss_maintainer_copilot.schemas.triage import (
    IssueTriageInput,
    IssueTriageResult,
    RepositoryMetadata,
)

__all__ = ["IssueTriageAgent", "build_triage_labels", "render_triage_markdown"]


class IssueTriageAgent:
    """Deterministic issue triage for GitHub maintainer workflows."""

    def __init__(
        self,
        signal_collector: IssueSignalCollector | None = None,
        scorer: IssueTriageScorer | None = None,
    ) -> None:
        self._signal_collector = signal_collector or IssueSignalCollector()
        self._scorer = scorer or IssueTriageScorer()

    def triage(self, issue: IssueTriageInput) -> IssueTriageResult:
        signals = self._signal_collector.collect(issue)
        decision = self._scorer.score(issue, signals)

        return IssueTriageResult(
            category=decision.category,
            difficulty=decision.difficulty,
            good_first_issue=decision.good_first_issue,
            confidence=decision.confidence,
            missing_context=decision.missing_context,
            reasoning=decision.reasoning,
        )

    @staticmethod
    def from_github_issue(
        issue: GitHubIssue,
        repository: GitHubRepository | None = None,
    ) -> IssueTriageInput:
        repo_metadata = None
        if repository is not None:
            repo_metadata = RepositoryMetadata(full_name=repository.full_name)

        return IssueTriageInput(
            title=issue.title,
            body=issue.body,
            labels=[label.name for label in issue.labels],
            repository=repo_metadata,
        )
