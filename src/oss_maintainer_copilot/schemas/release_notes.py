from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class VersionRange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    previous: str
    current: str


class MergedPullRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    labels: list[str] = Field(default_factory=list)
    author: str
    merge_date: str


class MarkdownSection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    entries: list[str] = Field(default_factory=list)
    markdown: str


class ReleaseNotesInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version_range: VersionRange
    merged_pull_requests: list[MergedPullRequest] = Field(default_factory=list)


class ReleaseNotesResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    release_title: str
    highlights: list[str] = Field(default_factory=list)
    grouped_markdown_sections: list[MarkdownSection] = Field(default_factory=list)
    breaking_changes_section: str
    contributor_acknowledgments: list[str] = Field(default_factory=list)
