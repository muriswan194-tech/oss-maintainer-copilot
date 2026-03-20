from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RepositoryArea(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str
    purpose: str
    contributor_entrypoint: str


class RepositoryIntelligenceInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository_name: str
    description: str = ""
    primary_language: str | None = None
    readme_text: str = ""
    contributing_text: str = ""
    setup_files: list[str] = Field(default_factory=list)
    top_level_paths: list[str] = Field(default_factory=list)


class RepositoryIntelligenceResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository_summary: str
    maintainer_workflows: list[str] = Field(default_factory=list)
    local_setup_steps: list[str] = Field(default_factory=list)
    major_areas: list[RepositoryArea] = Field(default_factory=list)
    good_starting_points: list[str] = Field(default_factory=list)
    contributor_checklist: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
