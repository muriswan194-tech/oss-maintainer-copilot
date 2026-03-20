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
TEST_PATH_PREFIXES = ("tests/",)
AUTOMATION_PATH_PREFIXES = (".github/workflows/",)
DEPENDENCY_FILE_NAMES = {
    "package-lock.json",
    "package.json",
    "pnpm-lock.yaml",
    "poetry.lock",
    "requirements-dev.txt",
    "requirements.txt",
    "yarn.lock",
}
CONFIG_FILE_NAMES = {
    ".pre-commit-config.yaml",
    "docker-compose.yml",
    "mkdocs.yml",
    "pyproject.toml",
}
RISKY_PATH_HINTS = (
    ".github/workflows/",
    "auth",
    "database",
    "migrations/",
    "permissions",
    "security",
    "deploy",
    "release",
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
    "deploy",
)
NOISY_FILE_THRESHOLD = 8
NOISY_COMMIT_THRESHOLD = 5
NOISY_AREA_THRESHOLD = 4
NOISY_DESCRIPTION_WORD_THRESHOLD = 180


@dataclass(frozen=True)
class PullRequestSignals:
    docs_only: bool
    risky_paths: list[str]
    risky_keywords: list[str]
    breaking_change: bool
    changed_areas: list[str]
    file_count: int
    commit_count: int
    noisy_context: bool
    broad_surface: bool
    input_warnings: list[str]


class PullRequestSummarizer:
    """Deterministic PR summarizer for maintainer review workflows."""

    def summarize(self, pull_request: PullRequestSummaryInput) -> PullRequestSummaryResult:
        signals = self._collect_signals(pull_request)
        review_focus = self._build_review_focus(signals)
        short_summary = self._build_short_summary(pull_request, signals)
        technical_summary = self._build_technical_summary(pull_request, signals)
        risk_assessment = self._build_risk_assessment(signals)
        reviewer_checklist = self._build_reviewer_checklist(signals, review_focus)
        release_note_snippet = self._build_release_note_snippet(pull_request, signals)

        return PullRequestSummaryResult(
            short_summary=short_summary,
            technical_summary=technical_summary,
            risk_assessment=risk_assessment,
            changed_areas=signals.changed_areas,
            review_focus=review_focus,
            input_warnings=signals.input_warnings,
            reviewer_checklist=reviewer_checklist,
            release_note_snippet=release_note_snippet,
        )

    def _collect_signals(self, pull_request: PullRequestSummaryInput) -> PullRequestSignals:
        combined_text = " ".join(
            [
                pull_request.title,
                pull_request.description,
                " ".join(pull_request.labels),
                *pull_request.commit_messages,
            ]
        ).casefold()
        normalized_paths = [
            path.replace("\\", "/") for path in pull_request.changed_file_paths
        ]
        changed_areas = self._infer_changed_areas(normalized_paths)
        docs_only = bool(normalized_paths) and changed_areas == ["documentation"]
        risky_paths = [
            path
            for path in normalized_paths
            if any(hint in path.casefold() for hint in RISKY_PATH_HINTS)
        ]
        risky_keywords = [
            keyword for keyword in RISKY_KEYWORDS if keyword in combined_text
        ]
        breaking_change = (
            "breaking" in {label.casefold() for label in pull_request.labels}
            or any(keyword in combined_text for keyword in BREAKING_KEYWORDS)
        )
        file_count = len(normalized_paths)
        commit_count = len(pull_request.commit_messages)
        broad_surface = len(changed_areas) >= 3 or file_count >= 6
        noisy_context = (
            file_count >= NOISY_FILE_THRESHOLD
            or commit_count >= NOISY_COMMIT_THRESHOLD
            or len(changed_areas) >= NOISY_AREA_THRESHOLD
            or len(pull_request.description.split()) >= NOISY_DESCRIPTION_WORD_THRESHOLD
        )

        input_warnings = self._build_input_warnings(
            pull_request,
            changed_areas,
            file_count,
            commit_count,
            noisy_context,
            broad_surface,
        )

        return PullRequestSignals(
            docs_only=docs_only,
            risky_paths=risky_paths,
            risky_keywords=risky_keywords,
            breaking_change=breaking_change,
            changed_areas=changed_areas,
            file_count=file_count,
            commit_count=commit_count,
            noisy_context=noisy_context,
            broad_surface=broad_surface,
            input_warnings=input_warnings,
        )

    def _infer_changed_areas(self, changed_file_paths: list[str]) -> list[str]:
        areas: list[str] = []
        for path in changed_file_paths:
            label = self._classify_path_area(path)
            if label not in areas:
                areas.append(label)
        return areas or ["project files"]

    def _classify_path_area(self, path: str) -> str:
        normalized = path.casefold()
        file_name = normalized.rsplit("/", maxsplit=1)[-1]

        if self._is_docs_path(path):
            return "documentation"
        if normalized.startswith(AUTOMATION_PATH_PREFIXES):
            return "automation"
        if normalized.startswith(TEST_PATH_PREFIXES):
            return "tests"
        if file_name in DEPENDENCY_FILE_NAMES:
            return "dependencies"
        if file_name in CONFIG_FILE_NAMES or normalized.endswith((".toml", ".yaml", ".yml")):
            return "configuration"
        if normalized.startswith("src/") or normalized.endswith(
            (".py", ".ts", ".tsx", ".js", ".jsx")
        ):
            return "application code"
        return "project files"

    def _is_docs_path(self, path: str) -> bool:
        normalized = path.casefold()
        file_name = normalized.rsplit("/", maxsplit=1)[-1]
        return (
            normalized.startswith(DOCS_PATH_PREFIXES)
            or file_name in DOCS_FILE_NAMES
            or normalized.endswith(".md")
        )

    def _build_input_warnings(
        self,
        pull_request: PullRequestSummaryInput,
        changed_areas: list[str],
        file_count: int,
        commit_count: int,
        noisy_context: bool,
        broad_surface: bool,
    ) -> list[str]:
        warnings: list[str] = []

        if noisy_context:
            warnings.append(
                f"Broad PR context: {file_count} files, {commit_count} commits, "
                f"{len(changed_areas)} changed areas."
            )
        if broad_surface and len(pull_request.description.split()) < 20:
            warnings.append(
                "The PR description is short relative to the breadth of the "
                "change surface."
            )
        if not pull_request.commit_messages and file_count >= 4:
            warnings.append(
                "Commit summaries are missing for a multi-file pull request."
            )

        return warnings

    def _build_review_focus(self, signals: PullRequestSignals) -> list[str]:
        focus: list[str] = []
        for area in signals.changed_areas:
            if area == "documentation":
                focus.append(
                    "Check contributor-facing instructions, wording, and links "
                    "for accuracy."
                )
            elif area == "automation":
                focus.append(
                    "Validate workflow triggers, permission scopes, and "
                    "comment or artifact handling."
                )
            elif area == "tests":
                focus.append(
                    "Confirm tests still reflect the intended workflow "
                    "contract."
                )
            elif area == "dependencies":
                focus.append(
                    "Review version changes, lockfile churn, and downstream "
                    "compatibility risk."
                )
            elif area == "configuration":
                focus.append(
                    "Check defaults, environment assumptions, and deployment "
                    "impact."
                )
            elif area == "application code":
                focus.append(
                    "Review runtime behavior, compatibility, and error "
                    "handling in the touched code."
                )
        if signals.noisy_context:
            focus.append(
                "Review in passes: high-risk areas first, then representative "
                "files from each remaining area."
            )
        return focus

    def _build_short_summary(
        self,
        pull_request: PullRequestSummaryInput,
        signals: PullRequestSignals,
    ) -> str:
        if signals.docs_only:
            return f"Documentation-only change: {pull_request.title.rstrip('.')}"
        if signals.breaking_change:
            return f"Breaking change: {pull_request.title.rstrip('.')}"
        areas = ", ".join(signals.changed_areas)
        if signals.noisy_context:
            return (
                f"Broad change across {areas} touching {signals.file_count} files."
            )
        return f"{pull_request.title.rstrip('.')} affecting {areas}."

    def _build_technical_summary(
        self,
        pull_request: PullRequestSummaryInput,
        signals: PullRequestSignals,
    ) -> str:
        areas = ", ".join(signals.changed_areas)
        commit_context = ""
        if pull_request.commit_messages:
            commit_context = (
                " Commits mention: "
                + "; ".join(pull_request.commit_messages[:3])
                + "."
            )

        if signals.docs_only:
            return (
                f"The PR updates {areas} only across {signals.file_count} files "
                "and does not appear to change runtime behavior."
                + commit_context
            )
        if signals.breaking_change:
            return (
                f"The PR changes {areas} and includes compatibility-sensitive "
                "language that suggests a migration or consumer update may "
                "be required."
                + commit_context
            )
        if signals.noisy_context:
            return (
                f"The PR spans {signals.file_count} files across {areas}. "
                "Reviewers should confirm that the stated scope matches the "
                "actual change surface before going file by file."
                + commit_context
            )
        if signals.risky_paths or signals.risky_keywords:
            return (
                f"The PR touches {areas} with paths or context that can affect "
                "runtime behavior, automation, or repository operations."
                + commit_context
            )
        return (
            f"The PR changes {areas} with no obvious compatibility warnings."
            + commit_context
        )

    def _build_risk_assessment(self, signals: PullRequestSignals) -> RiskAssessment:
        flags: list[str] = []
        if signals.breaking_change:
            flags.append("breaking-change-language")
        if signals.risky_paths:
            flags.append("risky-file-paths")
        if signals.risky_keywords:
            flags.append("risky-commit-context")
        if signals.broad_surface:
            flags.append("broad-change-surface")
        if signals.input_warnings:
            flags.append("noisy-pr-context")

        if signals.breaking_change:
            return RiskAssessment(
                level=RiskLevel.HIGH,
                summary=(
                    "High risk because the PR signals a breaking or "
                    "backward-incompatible change."
                ),
                flags=flags,
            )
        if signals.docs_only and not signals.input_warnings:
            return RiskAssessment(
                level=RiskLevel.LOW,
                summary="Low risk because the changed files are documentation-only.",
                flags=flags,
            )
        if (
            signals.risky_paths
            or signals.risky_keywords
            or "automation" in signals.changed_areas
        ):
            return RiskAssessment(
                level=RiskLevel.HIGH,
                summary=(
                    "High risk because the PR touches sensitive runtime or "
                    "automation areas."
                ),
                flags=flags,
            )
        if signals.noisy_context or signals.broad_surface:
            return RiskAssessment(
                level=RiskLevel.MEDIUM,
                summary=(
                    "Medium risk because the PR spans multiple areas or a "
                    "broader-than-usual change surface."
                ),
                flags=flags,
            )
        return RiskAssessment(
            level=RiskLevel.MEDIUM,
            summary=(
                "Medium risk because the PR changes code but does not "
                "advertise a breaking change."
            ),
            flags=flags,
        )

    def _build_reviewer_checklist(
        self,
        signals: PullRequestSignals,
        review_focus: list[str],
    ) -> list[str]:
        checklist = [
            "Verify the summary matches the actual code and commit intent.",
            "Confirm the changed-area labels match the touched files.",
        ]
        if signals.docs_only:
            checklist.extend(
                [
                    "Check that the documentation instructions are accurate "
                    "and link targets still resolve.",
                    "Confirm no code paths or automation behavior changed "
                    "alongside the docs update.",
                ]
            )
            return checklist

        if signals.input_warnings:
            checklist.append(
                "Start by checking whether the PR title and description "
                "understate the actual scope."
            )
            checklist.append(
                "Review high-risk or high-churn areas first before doing a "
                "line-by-line pass."
            )

        checklist.append("Review the touched files for unintended scope expansion.")

        for focus in review_focus[:3]:
            checklist.append(f"Focus review on: {focus}")

        if signals.breaking_change:
            checklist.append(
                "Confirm migration guidance and compatibility notes are documented."
            )
            checklist.append(
                "Validate versioning and release communication for the "
                "breaking change."
            )
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
        if signals.changed_areas == ["automation"]:
            return f"Maintenance: {title}"
        return f"Updated: {title}"


def render_pr_summary_markdown(
    pull_request: PullRequestSummaryInput,
    summary: PullRequestSummaryResult,
) -> str:
    checklist_lines = "\n".join(f"- {item}" for item in summary.reviewer_checklist)
    flag_lines = (
        "\n".join(f"- `{flag}`" for flag in summary.risk_assessment.flags) or "- None."
    )
    changed_area_lines = "\n".join(
        f"- `{area}`" for area in summary.changed_areas
    ) or "- None."
    review_focus_lines = "\n".join(
        f"- {item}" for item in summary.review_focus
    ) or "- None."
    warning_lines = "\n".join(
        f"- {item}" for item in summary.input_warnings
    ) or "- None."

    return f"""<!-- oss-maintainer-copilot:pr-summary -->
## OSS Maintainer Copilot PR Summary

**Title:** {pull_request.title}

### Short Summary
{summary.short_summary}

### Technical Summary
{summary.technical_summary}

### Changed Areas
{changed_area_lines}

### Input Warnings
{warning_lines}

### Risk Assessment
- Level: `{summary.risk_assessment.level.value}`
- Summary: {summary.risk_assessment.summary}

Flags:
{flag_lines}

### Review Focus
{review_focus_lines}

### Reviewer Checklist
{checklist_lines}

### Release Note Snippet
{summary.release_note_snippet}
"""
