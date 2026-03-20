"""Task-specific agents."""

from oss_maintainer_copilot.agents.good_first_issue import GoodFirstIssueAgent
from oss_maintainer_copilot.agents.issue_triage import IssueTriageAgent
from oss_maintainer_copilot.agents.onboarding_map import OnboardingMapAgent
from oss_maintainer_copilot.agents.pr_summary import PullRequestSummarizer
from oss_maintainer_copilot.agents.repo_intel import RepositoryIntelligenceAgent
from oss_maintainer_copilot.agents.release_notes import ReleaseNotesGenerator

__all__ = [
    "GoodFirstIssueAgent",
    "IssueTriageAgent",
    "OnboardingMapAgent",
    "PullRequestSummarizer",
    "ReleaseNotesGenerator",
    "RepositoryIntelligenceAgent",
]
