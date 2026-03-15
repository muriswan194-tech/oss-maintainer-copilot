from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GitHubUser(BaseModel):
    model_config = ConfigDict(extra="ignore")

    login: str


class GitHubLabel(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str


class GitHubRepository(BaseModel):
    model_config = ConfigDict(extra="ignore")

    full_name: str
    html_url: str | None = None


class GitHubIssue(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    title: str
    body: str = ""
    state: str | None = None
    html_url: str | None = None
    labels: list[GitHubLabel] = Field(default_factory=list)
    user: GitHubUser | None = None


class GitHubIssueEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: str | None = None
    issue: GitHubIssue
    repository: GitHubRepository | None = None


class GitHubPullRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")

    number: int
    title: str
    body: str = ""
    html_url: str | None = None
    merged_at: str | None = None
    labels: list[GitHubLabel] = Field(default_factory=list)
    user: GitHubUser | None = None


class GitHubPullRequestFile(BaseModel):
    model_config = ConfigDict(extra="ignore")

    filename: str


class GitHubPullRequestEnvelope(BaseModel):
    model_config = ConfigDict(extra="ignore")

    action: str | None = None
    pull_request: GitHubPullRequest
    repository: GitHubRepository | None = None
