from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from oss_maintainer_copilot.schemas.common import RiskLevel


class PullRequestSummaryInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: str = ""
    labels: list[str] = Field(default_factory=list)
    changed_file_paths: list[str] = Field(default_factory=list)
    commit_messages: list[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    model_config = ConfigDict(extra="forbid")

    level: RiskLevel
    summary: str
    flags: list[str] = Field(default_factory=list)


class PullRequestSummaryResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    short_summary: str
    technical_summary: str
    risk_assessment: RiskAssessment
    changed_areas: list[str] = Field(default_factory=list)
    review_focus: list[str] = Field(default_factory=list)
    input_warnings: list[str] = Field(default_factory=list)
    reviewer_checklist: list[str] = Field(default_factory=list)
    release_note_snippet: str
