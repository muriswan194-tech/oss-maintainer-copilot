from __future__ import annotations

from dataclasses import dataclass

from oss_maintainer_copilot.agents.triage_signals import IssueSignals
from oss_maintainer_copilot.schemas.common import DifficultyLevel, IssueCategory
from oss_maintainer_copilot.schemas.triage import IssueTriageInput, StructuredReasoning


@dataclass(frozen=True)
class TriageDecision:
    category: IssueCategory
    difficulty: DifficultyLevel
    good_first_issue: bool
    missing_context: list[str]
    reasoning: list[StructuredReasoning]
    confidence: float


class IssueTriageScorer:
    """Score triage signals into maintainer-facing decisions."""

    def score(self, issue: IssueTriageInput, signals: IssueSignals) -> TriageDecision:
        category = self._classify_category(signals)
        missing_context = self._detect_missing_context(issue, category, signals)
        difficulty = self._classify_difficulty(category, signals, missing_context)
        good_first_issue = self._is_good_first_issue(
            category,
            difficulty,
            signals,
            missing_context,
        )
        reasoning = self._build_reasoning(
            category,
            difficulty,
            good_first_issue,
            missing_context,
            signals,
        )
        confidence = self._calculate_confidence(category, missing_context, signals)

        return TriageDecision(
            category=category,
            difficulty=difficulty,
            good_first_issue=good_first_issue,
            missing_context=missing_context,
            reasoning=reasoning,
            confidence=confidence,
        )

    def _classify_category(self, signals: IssueSignals) -> IssueCategory:
        explicit_label_categories = self._explicit_label_categories(signals.labels)
        if len(explicit_label_categories) > 1:
            return IssueCategory.AMBIGUOUS

        top_category, top_score = max(
            signals.category_scores.items(),
            key=lambda item: item[1],
        )

        if top_score == 0:
            return IssueCategory.AMBIGUOUS

        tied_categories = [
            category
            for category, score in signals.category_scores.items()
            if score == top_score and score > 0
        ]
        if len(tied_categories) > 1:
            docs_labels = {"docs", "documentation"}
            featureish_labels = {
                "enhancement",
                "feature",
                "type: feature",
                "bug",
                "refactor",
                "technical debt",
            }
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

    def _explicit_label_categories(
        self,
        labels: set[str],
    ) -> set[IssueCategory]:
        categories: set[IssueCategory] = set()
        if labels.intersection({"bug", "type: bug"}):
            categories.add(IssueCategory.BUG)
        if labels.intersection({"docs", "documentation"}):
            categories.add(IssueCategory.DOCS)
        if labels.intersection({"enhancement", "feature", "type: feature"}):
            categories.add(IssueCategory.FEATURE_REQUEST)
        if labels.intersection({"refactor", "cleanup", "technical debt"}):
            categories.add(IssueCategory.REFACTOR)
        return categories

    def _detect_missing_context(
        self,
        issue: IssueTriageInput,
        category: IssueCategory,
        signals: IssueSignals,
    ) -> list[str]:
        missing_context: list[str] = []

        if signals.empty_body:
            missing_context.append("problem_statement")
        elif (
            signals.body_word_count < 20
            and category is not IssueCategory.DOCS
        ):
            missing_context.append("problem_statement")
        if (
            not signals.has_acceptance_criteria
            and category
            in {
                IssueCategory.FEATURE_REQUEST,
                IssueCategory.REFACTOR,
                IssueCategory.AMBIGUOUS,
            }
        ):
            missing_context.append("acceptance_criteria")
        if category is IssueCategory.BUG:
            if not signals.has_reproduction:
                missing_context.append("reproduction_steps")
            if not signals.has_expected_behavior:
                missing_context.append("expected_behavior")
        if (
            category is IssueCategory.DOCS
            and not self._has_explicit_docs_target(issue)
        ):
            missing_context.append("target_docs_location")
        if (
            category is IssueCategory.FEATURE_REQUEST
            and "because" not in issue.body.casefold()
        ):
            missing_context.append("user_need")
        if (
            category is IssueCategory.REFACTOR
            and not self._has_explicit_target_area(issue)
        ):
            missing_context.append("target_area")
        if category is IssueCategory.AMBIGUOUS:
            if not self._has_explicit_target_area(issue):
                missing_context.append("target_area")
            if (
                "why" not in issue.body.casefold()
                and "because" not in issue.body.casefold()
            ):
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
        if (
            category is IssueCategory.FEATURE_REQUEST
            and len(missing_context) <= 1
        ):
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
        return [
            StructuredReasoning(
                category="category",
                decision=category.value,
                evidence=self._category_evidence(category, signals),
                confidence=self._bounded_confidence(
                    0.65 + (0.08 * signals.category_scores[category])
                ),
            ),
            StructuredReasoning(
                category="difficulty",
                decision=difficulty.value,
                evidence=self._difficulty_evidence(
                    difficulty,
                    signals,
                    missing_context,
                ),
                confidence=self._bounded_confidence(
                    0.68 - (0.04 * len(missing_context))
                ),
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
                confidence=self._bounded_confidence(
                    0.72 - (0.05 * len(missing_context))
                ),
            ),
        ]

    def _category_evidence(
        self,
        category: IssueCategory,
        signals: IssueSignals,
    ) -> list[str]:
        scores = ", ".join(
            f"{issue_category.value}={score}"
            for issue_category, score in signals.category_scores.items()
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
            evidence.append(
                "High-risk terms: " + ", ".join(sorted(signals.high_risk_hits)) + "."
            )
        if missing_context:
            evidence.append(
                "Missing context fields: " + ", ".join(missing_context) + "."
            )
        if (
            not signals.high_risk_hits
            and not missing_context
            and difficulty is DifficultyLevel.BEGINNER
        ):
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
            evidence.append(
                "Missing context prevents a safe first-contribution handoff."
            )
        if signals.high_risk_hits:
            evidence.append(
                "High-risk terms make the issue unsuitable for first-time "
                "contributors."
            )
        if not good_first_issue:
            evidence.append(
                "Good first issue requires low-risk, narrow, well-specified work."
            )
        else:
            evidence.append(
                "The issue is explicit, low-risk, and scoped tightly enough "
                "for onboarding."
            )
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

    def _has_explicit_target_area(self, issue: IssueTriageInput) -> bool:
        text = " ".join([issue.title, issue.body]).casefold()
        explicit_markers = (
            "target file",
            "target module",
            "target path",
            "component:",
            "module:",
            "file:",
            "src/",
            "docs/",
            ".py",
            ".md",
            ".yml",
            ".yaml",
            ".toml",
            "readme",
            "contributing",
        )
        return any(marker in text for marker in explicit_markers)

    def _has_explicit_docs_target(self, issue: IssueTriageInput) -> bool:
        text = " ".join([issue.title, issue.body]).casefold()
        docs_markers = (
            "target file",
            "readme",
            "contributing",
            "docs/",
            ".md",
        )
        return any(marker in text for marker in docs_markers)
