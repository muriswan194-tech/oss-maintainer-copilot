from __future__ import annotations

from dataclasses import dataclass

from oss_maintainer_copilot.schemas.common import RiskLevel
from oss_maintainer_copilot.schemas.pull_request import (
    PullRequestSummaryInput,
    PullRequestSummaryResult,
    RiskAssessment,
)

DOCS_PATH_PREFIXES = ("docs/",)
DOCS_FILE_NAMES = {"readme.md", "contributing.md", "roadmap.md", "agents.md"}
RISKY_PATH_HINTS = (
    ".github/workflows/",
    "auth",
    "database",
    "migrations/",
    "permissions",
    "security",
    "src/",
)
BREAKING_KEYWORDS = (
    "breaking",
    "backward incompatible",
    "drop support",
    "migration required",
    "remove",
    "rename",
)
RISKY_KEYWORDS = (
    "auth",
    "database",
    "migration",
    "permissions",
    "security",
    "workflow",
)


@dataclass(frozen=True)
class PullRequestSignals:
    docs_only: bool
    risky_paths: list[str]
    risky_keywords: list[str]
    breaking_change: bool
    changed_area_labels: list[str]


class PullRequestSummarizer:
    """Deterministic PR summarizer for maintainer review workflows."""

    def summarize(self, pull_request: PullRequestSummaryInput) -> PullRequestSummaryResult:
        signals = self._collect_signals(pull_request)
        short_summary = self._build_short_summary(pull_request, signals)
        technical_summary = self._build_technical_summary(pull_request, signals)
        risk_assessment = self._build_risk_assessment(signals)
        reviewer_checklist = self._build_reviewer_checklist(signals)
        release_note_snippet = self._build_release_note_snippet(pull_request, signals)

        return PullRequestSummaryResult(
            short_summary=short_summary,
            technical_summary=technical_summary,
            risk_assessment=risk_assessment,
            reviewer_checklist=reviewer_checklist,
            release_note_snippet=release_note_snippet,
        )

    def _collect_signals(self, pull_request: PullRequestSummaryInput) -> PullRequestSignals:
        combined_text = " ".join(
            [pull_request.title, pull_request.description, *pull_request.commit_messages]
        ).casefold()
        normalized_paths = [path.replace("\\", "/") for path in pull_request.changed_file_paths]
        docs_only = bool(normalized_paths) and all(self._is_docs_path(path) for path in normalized_paths)
        risky_paths = [path for path in normalized_paths if any(hint in path.casefold() for hint in RISKY_PATH_HINTS)]
        risky_keywords = [keyword for keyword in RISKY_KEYWORDS if keyword in combined_text]
        breaking_change = any(keyword in combined_text for keyword in BREAKING_KEYWORDS)
        changed_area_labels = self._infer_changed_areas(normalized_paths)

        return PullRequestSignals(
            docs_only=docs_only,
            risky_paths=risky_paths,
            risky_keywords=risky_keywords,
            breaking_change=breaking_change,
            changed_area_labels=changed_area_labels,
        )

    def _is_docs_path(self, path: str) -> bool:
        normalized = path.casefold()
        file_name = normalized.rsplit("/", maxsplit=1)[-1]
        return (
            normalized.startswith(DOCS_PATH_PREFIXES)
            or file_name in DOCS_FILE_NAMES
            or normalized.endswith(".md")
        )

    def _infer_changed_areas(self, changed_file_paths: list[str]) -> list[str]:
        areas: list[str] = []
        for path in changed_file_paths:
            normalized = path.casefold()
            if self._is_docs_path(path):
                label = "documentation"
            elif normalized.startswith(".github/workflows/"):
                label = "automation"
            elif normalized.startswith("tests/"):
                label = "tests"
            elif normalized.startswith("src/"):
                label = "application code"
            else:
                label = "project files"

            if label not in areas:
                areas.append(label)
        return areas or ["project files"]

    def _build_short_summary(
        self,
        pull_request: PullRequestSummaryInput,
        signals: PullRequestSignals,
    ) -> str:
        if signals.docs_only:
            return f"Documentation-only change: {pull_request.title.rstrip('.')}"
        if signals.breaking_change:
            return f"Breaking change: {pull_request.title.rstrip('.')}"
        areas = ", ".join(signals.changed_area_labels)
        return f"{pull_request.title.rstrip('.')} affecting {areas}."

    def _build_technical_summary(
        self,
        pull_request: PullRequestSummaryInput,
        signals: PullRequestSignals,
    ) -> str:
        areas = ", ".join(signals.changed_area_labels)
        commit_context = ""
        if pull_request.commit_messages:
            commit_context = " Commits mention: " + "; ".join(pull_request.commit_messages[:3]) + "."

        if signals.docs_only:
            return (
                f"The PR updates {areas} only and does not appear to change runtime behavior."
                + commit_context
            )
        if signals.breaking_change:
            return (
                f"The PR changes {areas} and includes compatibility-sensitive language that suggests a migration "
                f"or consumer update may be required."
                + commit_context
            )
        if signals.risky_paths or signals.risky_keywords:
            return (
                f"The PR touches {areas} with code paths that can affect runtime behavior or automation."
                + commit_context
            )
        return f"The PR changes {areas} with no obvious compatibility warnings." + commit_context

    def _build_risk_assessment(self, signals: PullRequestSignals) -> RiskAssessment:
        flags: list[str] = []
        if signals.breaking_change:
            flags.append("breaking-change-language")
        if signals.risky_paths:
            flags.append("risky-file-paths")
        if signals.risky_keywords:
            flags.append("risky-commit-context")

        if signals.breaking_change:
            return RiskAssessment(
                level=RiskLevel.HIGH,
                summary="High risk because the PR signals a breaking or backward-incompatible change.",
                flags=flags,
            )
        if signals.docs_only:
            return RiskAssessment(
                level=RiskLevel.LOW,
                summary="Low risk because the changed files are documentation-only.",
                flags=flags,
            )
        if signals.risky_paths or signals.risky_keywords:
            return RiskAssessment(
                level=RiskLevel.HIGH,
                summary="High risk because the PR touches sensitive runtime or automation areas.",
                flags=flags,
            )
        return RiskAssessment(
            level=RiskLevel.MEDIUM,
            summary="Medium risk because the PR changes code but does not advertise a breaking change.",
            flags=flags,
        )

    def _build_reviewer_checklist(self, signals: PullRequestSignals) -> list[str]:
        checklist = [
            "Verify the summary matches the actual code and commit intent.",
        ]
        if signals.docs_only:
            checklist.extend(
                [
                    "Check that the documentation instructions are accurate and link targets still resolve.",
                    "Confirm no code paths or automation behavior changed alongside the docs update.",
                ]
            )
            return checklist

        checklist.append("Review the touched files for unintended scope expansion.")
        if signals.risky_paths:
            checklist.append("Exercise the sensitive code paths or workflows touched by the PR.")
        if signals.breaking_change:
            checklist.append("Confirm migration guidance and compatibility notes are documented.")
            checklist.append("Validate versioning and release communication for the breaking change.")
        else:
            checklist.append("Confirm tests cover the changed runtime behavior.")
        return checklist

    def _build_release_note_snippet(
        self,
        pull_request: PullRequestSummaryInput,
        signals: PullRequestSignals,
    ) -> str:
        title = pull_request.title.rstrip(".")
        if signals.breaking_change:
            return f"Breaking: {title}"
        if signals.docs_only:
            return f"Docs: {title}"
        return f"Updated: {title}"


def render_pr_summary_markdown(
    pull_request: PullRequestSummaryInput,
    summary: PullRequestSummaryResult,
) -> str:
    checklist_lines = "\n".join(f"- {item}" for item in summary.reviewer_checklist)
    flag_lines = "\n".join(f"- `{flag}`" for flag in summary.risk_assessment.flags) or "- None."
    return f"""<!-- oss-maintainer-copilot:pr-summary -->
## OSS Maintainer Copilot PR Summary

**Title:** {pull_request.title}

### Short Summary
{summary.short_summary}

### Technical Summary
{summary.technical_summary}

### Risk Assessment
- Level: `{summary.risk_assessment.level.value}`
- Summary: {summary.risk_assessment.summary}

Flags:
{flag_lines}

### Reviewer Checklist
{checklist_lines}

### Release Note Snippet
{summary.release_note_snippet}
"""
