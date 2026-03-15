from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class GoodFirstIssueResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    eligible: bool
    confidence: float = Field(ge=0.0, le=1.0)
    matched_signals: list[str] = Field(default_factory=list)
    blocked_by: list[str] = Field(default_factory=list)
    reasoning: list[str] = Field(default_factory=list)
