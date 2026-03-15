from __future__ import annotations

from dataclasses import dataclass

from oss_maintainer_copilot.schemas.common import DifficultyLevel, IssueCategory
from oss_maintainer_copilot.schemas.github import GitHubIssue, GitHubRepository
from oss_maintainer_copilot.schemas.triage import (
    IssueTriageInput,
    IssueTriageResult,
    RepositoryMetadata,
    StructuredReasoning,
)

BUG_KEYWORDS = {
    "bug",
    "crash",
    "error",
    "fail",
    "failing",
    "incorrect",
    "regression",
    "traceback",
}
DOCS_KEYWORDS = {
    "docs",
    "documentation",
    "guide",
    "readme",
    "tutorial",
    "typo",
}
FEATURE_KEYWORDS = {
    "allow",
    "enhancement",
    "feature",
    "new",
    "request",
    "support",
}
REFACTOR_KEYWORDS = {
    "cleanup",
    "extract",
    "refactor",
    "reorganize",
    "rename",
    "simplify",
    "technical debt",
}
HIGH_RISK_KEYWORDS = {
    "architecture",
    "authentication",
    "backward compatibility",
    "breaking",
    "compliance",
    "database",
    "migration",
    "performance",
    "release process",
    "security",
}
SURFACE_AREA_HINTS = {
    "api",
    "cli",
    "database",
    "docs",
    "documentation",
    "frontend",
    "workflow",
}
REPRODUCTION_HINTS = {"reproduce", "steps to reproduce", "actual behavior", "expected behavior"}
ACCEPTANCE_HINTS = {"acceptance criteria", "done when", "success criteria"}
TARGET_HINTS = {"file", "module", "component", "readme", "workflow", "tests", "docs"}


@dataclass(frozen=True)
class IssueSignals:
    category_scores: dict[IssueCategory, int]
    high_risk_hits: set[str]
    surface_area_hits: set[str]
    body_word_count: int
    labels: set[str]
    has_reproduction: bool
    has_expected_behavior: bool
    has_acceptance_criteria: bool
    has_target_area: bool
    empty_body: bool


class IssueTriageAgent:
    """Deterministic issue triage for GitHub maintainer workflows."""

    def triage(self, issue: IssueTriageInput) -> IssueTriageResult:
        signals = self._collect_signals(issue)
        category = self._classify_category(signals)
        missing_context = self._detect_missing_context(issue, category, signals)
        difficulty = self._classify_difficulty(category, signals, missing_context)
        good_first_issue = self._is_good_first_issue(category, difficulty, signals, missing_context)
        reasoning = self._build_reasoning(category, difficulty, good_first_issue, missing_context, signals)
        confidence = self._calculate_confidence(category, missing_context, signals)

        return IssueTriageResult(
            category=category,
            difficulty=difficulty,
            good_first_issue=good_first_issue,
            confidence=confidence,
            missing_context=missing_context,
            reasoning=reasoning,
        )

    @staticmethod
    def from_github_issue(issue: GitHubIssue, repository: GitHubRepository | None = None) -> IssueTriageInput:
        repo_metadata = None
        if repository is not None:
            repo_metadata = RepositoryMetadata(full_name=repository.full_name)

        return IssueTriageInput(
            title=issue.title,
            body=issue.body,
            labels=[label.name for label in issue.labels],
            repository=repo_metadata,
        )

    def _collect_signals(self, issue: IssueTriageInput) -> IssueSignals:
        text = self._normalize(issue.title, issue.body, issue.labels, issue.repository)
        labels = {label.casefold() for label in issue.labels}
        category_scores = {
            IssueCategory.BUG: self._keyword_score(text, labels, BUG_KEYWORDS, {"bug", "type: bug"}),
            IssueCategory.DOCS: self._keyword_score(text, labels, DOCS_KEYWORDS, {"docs", "documentation"}),
            IssueCategory.FEATURE_REQUEST: self._keyword_score(
                text,
                labels,
                FEATURE_KEYWORDS,
                {"enhancement", "feature", "type: feature"},
            ),
            IssueCategory.REFACTOR: self._keyword_score(
                text,
                labels,
                REFACTOR_KEYWORDS,
                {"refactor", "cleanup", "technical debt"},
            ),
            IssueCategory.AMBIGUOUS: 0,
        }

        return IssueSignals(
            category_scores=category_scores,
            high_risk_hits={keyword for keyword in HIGH_RISK_KEYWORDS if keyword in text},
            surface_area_hits={keyword for keyword in SURFACE_AREA_HINTS if keyword in text},
            body_word_count=len(issue.body.split()),
            labels=labels,
            has_reproduction=any(hint in text for hint in REPRODUCTION_HINTS),
            has_expected_behavior="expected behavior" in text or "expected" in text,
            has_acceptance_criteria=any(hint in text for hint in ACCEPTANCE_HINTS),
            has_target_area=any(hint in text for hint in TARGET_HINTS),
            empty_body=issue.body.strip() == "",
        )

    def _normalize(
        self,
        title: str,
        body: str,
        labels: list[str],
        repository: RepositoryMetadata | None,
    ) -> str:
        repo_text = ""
        if repository is not None:
            repo_text = " ".join(
                value
                for value in [repository.full_name or "", repository.primary_language or "", *repository.topics]
                if value
            )
        return " ".join([title, body, " ".join(labels), repo_text]).casefold()

    def _keyword_score(
        self,
        text: str,
        labels: set[str],
        keywords: set[str],
        label_matches: set[str],
    ) -> int:
        keyword_hits = sum(1 for keyword in keywords if keyword in text)
        label_hits = sum(2 for label in label_matches if label in labels)
        return keyword_hits + label_hits

    def _classify_category(self, signals: IssueSignals) -> IssueCategory:
        top_category, top_score = max(
            signals.category_scores.items(),
            key=lambda item: item[1],
        )

        if top_score == 0:
            return IssueCategory.AMBIGUOUS

        tied_categories = [
            category for category, score in signals.category_scores.items() if score == top_score and score > 0
        ]
        if len(tied_categories) > 1:
            docs_labels = {"docs", "documentation"}
            featureish_labels = {"enhancement", "feature", "type: feature", "bug", "refactor", "technical debt"}
            if (
                IssueCategory.DOCS in tied_categories
                and not signals.labels.intersection(featureish_labels)
                and (
                    signals.labels.intersection(docs_labels)
                    or signals.category_scores[IssueCategory.DOCS] > 0
                )
            ):
                return IssueCategory.DOCS
            return IssueCategory.AMBIGUOUS

        return top_category

    def _detect_missing_context(
        self,
        issue: IssueTriageInput,
        category: IssueCategory,
        signals: IssueSignals,
    ) -> list[str]:
        missing_context: list[str] = []

        if signals.empty_body or signals.body_word_count < 20:
            missing_context.append("problem_statement")
        if not signals.has_acceptance_criteria and category in {
            IssueCategory.FEATURE_REQUEST,
            IssueCategory.REFACTOR,
            IssueCategory.AMBIGUOUS,
        }:
            missing_context.append("acceptance_criteria")
        if category is IssueCategory.BUG:
            if not signals.has_reproduction:
                missing_context.append("reproduction_steps")
            if not signals.has_expected_behavior:
                missing_context.append("expected_behavior")
        if category is IssueCategory.DOCS and not signals.has_target_area:
            missing_context.append("target_docs_location")
        if category is IssueCategory.FEATURE_REQUEST and "because" not in issue.body.casefold():
            missing_context.append("user_need")
        if category is IssueCategory.REFACTOR and not signals.has_target_area:
            missing_context.append("target_area")
        if category is IssueCategory.AMBIGUOUS:
            if not signals.has_target_area:
                missing_context.append("target_area")
            if "why" not in issue.body.casefold() and "because" not in issue.body.casefold():
                missing_context.append("motivation")

        return missing_context

    def _classify_difficulty(
        self,
        category: IssueCategory,
        signals: IssueSignals,
        missing_context: list[str],
    ) -> DifficultyLevel:
        if signals.high_risk_hits:
            return DifficultyLevel.MAINTAINER_ONLY
        if category is IssueCategory.DOCS and len(missing_context) <= 1:
            return DifficultyLevel.BEGINNER
        if len(signals.surface_area_hits) >= 3 or signals.body_word_count > 250:
            return DifficultyLevel.ADVANCED
        if missing_context and category is IssueCategory.AMBIGUOUS:
            return DifficultyLevel.ADVANCED
        if category in {IssueCategory.BUG, IssueCategory.REFACTOR} and not missing_context:
            return DifficultyLevel.INTERMEDIATE
        if category is IssueCategory.FEATURE_REQUEST and len(missing_context) <= 1:
            return DifficultyLevel.INTERMEDIATE
        if category is IssueCategory.AMBIGUOUS:
            return DifficultyLevel.ADVANCED
        return DifficultyLevel.INTERMEDIATE

    def _is_good_first_issue(
        self,
        category: IssueCategory,
        difficulty: DifficultyLevel,
        signals: IssueSignals,
        missing_context: list[str],
    ) -> bool:
        if difficulty is not DifficultyLevel.BEGINNER:
            return False
        if category is IssueCategory.AMBIGUOUS:
            return False
        if missing_context:
            return False
        if signals.high_risk_hits or len(signals.surface_area_hits) > 1:
            return category is IssueCategory.DOCS and not signals.high_risk_hits
        return True

    def _build_reasoning(
        self,
        category: IssueCategory,
        difficulty: DifficultyLevel,
        good_first_issue: bool,
        missing_context: list[str],
        signals: IssueSignals,
    ) -> list[StructuredReasoning]:
        reasoning = [
            StructuredReasoning(
                category="category",
                decision=category.value,
                evidence=self._category_evidence(category, signals),
                confidence=self._bounded_confidence(0.65 + (0.08 * signals.category_scores[category])),
            ),
            StructuredReasoning(
                category="difficulty",
                decision=difficulty.value,
                evidence=self._difficulty_evidence(difficulty, signals, missing_context),
                confidence=self._bounded_confidence(0.68 - (0.04 * len(missing_context))),
            ),
            StructuredReasoning(
                category="good_first_issue",
                decision=str(good_first_issue).lower(),
                evidence=self._good_first_issue_evidence(
                    category,
                    difficulty,
                    good_first_issue,
                    signals,
                    missing_context,
                ),
                confidence=self._bounded_confidence(0.72 - (0.05 * len(missing_context))),
            ),
        ]
        return reasoning

    def _category_evidence(self, category: IssueCategory, signals: IssueSignals) -> list[str]:
        scores = ", ".join(
            f"{issue_category.value}={score}" for issue_category, score in signals.category_scores.items()
        )
        evidence = [f"Category scores: {scores}."]
        if signals.labels:
            evidence.append("Existing labels: " + ", ".join(sorted(signals.labels)) + ".")
        return evidence

    def _difficulty_evidence(
        self,
        difficulty: DifficultyLevel,
        signals: IssueSignals,
        missing_context: list[str],
    ) -> list[str]:
        evidence = [
            f"Detected {len(signals.surface_area_hits)} cross-cutting area hints.",
            f"Issue body length is about {signals.body_word_count} words.",
        ]
        if signals.high_risk_hits:
            evidence.append("High-risk terms: " + ", ".join(sorted(signals.high_risk_hits)) + ".")
        if missing_context:
            evidence.append("Missing context fields: " + ", ".join(missing_context) + ".")
        if not signals.high_risk_hits and not missing_context and difficulty is DifficultyLevel.BEGINNER:
            evidence.append("The issue is narrowly scoped and already well specified.")
        return evidence

    def _good_first_issue_evidence(
        self,
        category: IssueCategory,
        difficulty: DifficultyLevel,
        good_first_issue: bool,
        signals: IssueSignals,
        missing_context: list[str],
    ) -> list[str]:
        evidence = [
            f"Category is {category.value}.",
            f"Difficulty is {difficulty.value}.",
        ]
        if missing_context:
            evidence.append("Missing context prevents a safe first-contribution handoff.")
        if signals.high_risk_hits:
            evidence.append("High-risk terms make the issue unsuitable for first-time contributors.")
        if not good_first_issue:
            evidence.append("Good first issue requires low-risk, narrow, well-specified work.")
        else:
            evidence.append("The issue is explicit, low-risk, and scoped tightly enough for onboarding.")
        return evidence

    def _calculate_confidence(
        self,
        category: IssueCategory,
        missing_context: list[str],
        signals: IssueSignals,
    ) -> float:
        confidence = 0.62
        confidence += min(signals.category_scores[category] * 0.06, 0.18)
        confidence += 0.06 if signals.has_target_area else 0.0
        confidence += 0.05 if signals.has_acceptance_criteria else 0.0
        confidence -= min(len(missing_context) * 0.08, 0.24)
        if category is IssueCategory.AMBIGUOUS:
            confidence -= 0.08
        return round(self._bounded_confidence(confidence), 2)

    def _bounded_confidence(self, value: float) -> float:
        return min(max(value, 0.0), 0.99)


def build_triage_labels(result: IssueTriageResult) -> list[str]:
    labels = [
        f"triage:category:{result.category.value}",
        f"difficulty:{result.difficulty.value}",
    ]
    if result.good_first_issue:
        labels.append("triage:good-first-issue")
    if result.missing_context:
        labels.append("triage:missing-context")
    return labels


def render_triage_markdown(issue: IssueTriageInput, triage: IssueTriageResult) -> str:
    reasoning_lines = "\n".join(
        f"- **{item.category}**: `{item.decision}` ({'; '.join(item.evidence)})"
        for item in triage.reasoning
    )
    missing_context_lines = "\n".join(f"- `{item}`" for item in triage.missing_context) or "- None."

    return f"""<!-- oss-maintainer-copilot:issue-triage -->
## OSS Maintainer Copilot Triage

**Issue:** {issue.title}

### Classification

- Category: `{triage.category.value}`
- Difficulty: `{triage.difficulty.value}`
- Good first issue: `{str(triage.good_first_issue).lower()}`
- Confidence: `{triage.confidence:.2f}`

### Missing Context

{missing_context_lines}

### Structured Reasoning

{reasoning_lines}
"""
