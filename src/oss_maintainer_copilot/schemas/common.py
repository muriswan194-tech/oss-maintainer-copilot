from __future__ import annotations

from enum import StrEnum


class DifficultyLevel(StrEnum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MAINTAINER_ONLY = "maintainer_only"


class IssueCategory(StrEnum):
    BUG = "bug"
    DOCS = "docs"
    FEATURE_REQUEST = "feature_request"
    REFACTOR = "refactor"
    AMBIGUOUS = "ambiguous"


class ScopeLevel(StrEnum):
    NARROW = "narrow"
    MODERATE = "moderate"
    BROAD = "broad"


class RiskLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ContextLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
