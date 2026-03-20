from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from oss_maintainer_copilot.schemas.github import (
    GitHubIssue,
    GitHubIssueEnvelope,
    GitHubPullRequest,
    GitHubPullRequestEnvelope,
)
from oss_maintainer_copilot.schemas.pull_request import PullRequestSummaryInput
from oss_maintainer_copilot.schemas.repo_intel import RepositoryIntelligenceInput
from oss_maintainer_copilot.schemas.release_notes import ReleaseNotesInput


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_issue_envelope(path: Path) -> GitHubIssueEnvelope:
    return parse_issue_envelope(_load_json(path))


def parse_issue_envelope(payload: dict[str, Any]) -> GitHubIssueEnvelope:
    if "issue" in payload:
        return GitHubIssueEnvelope.model_validate(payload)
    return GitHubIssueEnvelope(issue=GitHubIssue.model_validate(payload))


def load_pull_request_envelope(path: Path) -> GitHubPullRequestEnvelope:
    return parse_pull_request_envelope(_load_json(path))


def parse_pull_request_envelope(payload: dict[str, Any]) -> GitHubPullRequestEnvelope:
    if "pull_request" in payload:
        return GitHubPullRequestEnvelope.model_validate(payload)
    return GitHubPullRequestEnvelope(pull_request=GitHubPullRequest.model_validate(payload))


def load_pull_request_summary_input(path: Path) -> PullRequestSummaryInput:
    payload = _load_json(path)
    if "pull_request" in payload:
        pull_request = parse_pull_request_envelope(payload).pull_request
        return PullRequestSummaryInput(
            title=pull_request.title,
            description=pull_request.body,
            labels=[label.name for label in pull_request.labels],
            changed_file_paths=payload.get("changed_file_paths", []),
            commit_messages=payload.get("commit_messages", []),
        )
    return PullRequestSummaryInput.model_validate(payload)


def load_release_notes_input(path: Path) -> ReleaseNotesInput:
    return ReleaseNotesInput.model_validate(_load_json(path))


def load_repo_intel_input(path: Path) -> RepositoryIntelligenceInput:
    return RepositoryIntelligenceInput.model_validate(_load_json(path))
