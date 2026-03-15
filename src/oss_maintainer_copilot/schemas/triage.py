from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from oss_maintainer_copilot.schemas.common import DifficultyLevel, IssueCategory


class StructuredReasoning(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str
    decision: str
    evidence: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)


class RepositoryMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = None
    primary_language: str | None = None
    topics: list[str] = Field(default_factory=list)


class IssueTriageInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    body: str = ""
    labels: list[str] = Field(default_factory=list)
    repository: RepositoryMetadata | None = None


class IssueTriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: IssueCategory
    difficulty: DifficultyLevel
    good_first_issue: bool
    confidence: float = Field(ge=0.0, le=1.0)
    missing_context: list[str] = Field(default_factory=list)
    reasoning: list[StructuredReasoning] = Field(default_factory=list)
