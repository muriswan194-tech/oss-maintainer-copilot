from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class SetupCheckpoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    command: str
    purpose: str
    success_signal: str


class OnboardingStep(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    objective: str
    paths: list[str] = Field(default_factory=list)
    completion_signal: str


class ContributorTrack(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    fit_for: str
    first_reads: list[str] = Field(default_factory=list)
    first_tasks: list[str] = Field(default_factory=list)


class StarterTask(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    reason: str
    suggested_paths: list[str] = Field(default_factory=list)
    difficulty: str


class OnboardingMapResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository_summary: str
    first_session_goal: str
    setup_checkpoints: list[SetupCheckpoint] = Field(default_factory=list)
    reading_order: list[OnboardingStep] = Field(default_factory=list)
    contributor_tracks: list[ContributorTrack] = Field(default_factory=list)
    starter_tasks: list[StarterTask] = Field(default_factory=list)
    escalation_notes: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
