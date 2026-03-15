from __future__ import annotations

from collections import defaultdict
from datetime import date

from oss_maintainer_copilot.schemas.release_notes import (
    MarkdownSection,
    MergedPullRequest,
    ReleaseNotesInput,
    ReleaseNotesResult,
)

SECTION_ORDER = [
    ("features", "Features"),
    ("fixes", "Fixes"),
    ("docs", "Documentation"),
    ("refactors", "Refactors"),
]

LABEL_GROUPS = {
    "breaking": "breaking",
    "bug": "fixes",
    "bugfix": "fixes",
    "docs": "docs",
    "documentation": "docs",
    "enhancement": "features",
    "feature": "features",
    "fix": "fixes",
    "refactor": "refactors",
}

HIGHLIGHT_LABELS = {"breaking", "feature", "enhancement"}
BREAKING_KEYWORDS = ("breaking", "migration", "deprecated", "drop support", "rename")


class ReleaseNotesGenerator:
    """Builds draft-ready GitHub release notes from merged pull request metadata."""

    def generate(self, release: ReleaseNotesInput) -> ReleaseNotesResult:
        sections = self._group_pull_requests(release.merged_pull_requests)
        highlights = self._build_highlights(release.merged_pull_requests)
        grouped_markdown_sections = self._build_markdown_sections(sections)
        breaking_changes_section = self._build_breaking_changes_section(release.merged_pull_requests)
        contributor_acknowledgments = self._build_contributor_acknowledgments(release.merged_pull_requests)
        release_title = self._build_release_title(release)

        return ReleaseNotesResult(
            release_title=release_title,
            highlights=highlights,
            grouped_markdown_sections=grouped_markdown_sections,
            breaking_changes_section=breaking_changes_section,
            contributor_acknowledgments=contributor_acknowledgments,
        )

    def render_markdown(self, result: ReleaseNotesResult) -> str:
        highlight_lines = "\n".join(f"- {item}" for item in result.highlights) or "- No headline changes in this release."
        sections_markdown = "\n\n".join(section.markdown for section in result.grouped_markdown_sections)
        acknowledgments = "\n".join(f"- {line}" for line in result.contributor_acknowledgments)
        return f"""# {result.release_title}

## Highlights
{highlight_lines}

{sections_markdown}

## Breaking Changes
{result.breaking_changes_section}

## Thanks
{acknowledgments}
"""

    def _build_release_title(self, release: ReleaseNotesInput) -> str:
        today = date.today().isoformat()
        return (
            f"{release.version_range.current} ({release.version_range.previous} -> "
            f"{release.version_range.current}) - {today}"
        )

    def _group_pull_requests(
        self,
        pull_requests: list[MergedPullRequest],
    ) -> dict[str, list[MergedPullRequest]]:
        grouped: dict[str, list[MergedPullRequest]] = defaultdict(list)
        for pull_request in pull_requests:
            grouped[self._categorize_pull_request(pull_request)].append(pull_request)
        return grouped

    def _categorize_pull_request(self, pull_request: MergedPullRequest) -> str:
        labels = {label.casefold() for label in pull_request.labels}
        title_text = pull_request.title.casefold()

        if "breaking" in labels or any(keyword in title_text for keyword in BREAKING_KEYWORDS):
            return "breaking"

        for label, group in LABEL_GROUPS.items():
            if label in labels:
                return group

        if "docs" in title_text or "readme" in title_text:
            return "docs"
        if "fix" in title_text or "bug" in title_text:
            return "fixes"
        if "refactor" in title_text or "cleanup" in title_text:
            return "refactors"
        return "features"

    def _build_highlights(self, pull_requests: list[MergedPullRequest]) -> list[str]:
        highlights: list[str] = []
        for pull_request in pull_requests:
            labels = {label.casefold() for label in pull_request.labels}
            title = self._clean_title(pull_request.title)
            if "breaking" in labels or any(keyword in title.casefold() for keyword in BREAKING_KEYWORDS):
                highlights.append(f"Breaking change: {title}.")
            elif labels.intersection(HIGHLIGHT_LABELS):
                highlights.append(f"{title}.")

        if not highlights and pull_requests:
            highlights.append(f"Includes {len(pull_requests)} merged pull requests across this release window.")

        return highlights[:4]

    def _build_markdown_sections(
        self,
        sections: dict[str, list[MergedPullRequest]],
    ) -> list[MarkdownSection]:
        markdown_sections: list[MarkdownSection] = []
        for key, title in SECTION_ORDER:
            pull_requests = sections.get(key, [])
            if not pull_requests:
                continue
            entries = [self._format_section_entry(pull_request) for pull_request in pull_requests]
            markdown = "## " + title + "\n" + "\n".join(f"- {entry}" for entry in entries)
            markdown_sections.append(MarkdownSection(title=title, entries=entries, markdown=markdown))
        return markdown_sections

    def _build_breaking_changes_section(self, pull_requests: list[MergedPullRequest]) -> str:
        breaking_entries = [
            self._format_breaking_entry(pull_request)
            for pull_request in pull_requests
            if self._categorize_pull_request(pull_request) == "breaking"
        ]
        if not breaking_entries:
            return "No breaking changes were identified in this release range."
        return "\n".join(f"- {entry}" for entry in breaking_entries)

    def _build_contributor_acknowledgments(
        self,
        pull_requests: list[MergedPullRequest],
    ) -> list[str]:
        contributions: dict[str, int] = defaultdict(int)
        for pull_request in pull_requests:
            contributions[pull_request.author] += 1

        acknowledgments = [
            f"@{author} contributed {count} merged pull request{'s' if count != 1 else ''}."
            for author, count in sorted(contributions.items(), key=lambda item: (-item[1], item[0].casefold()))
        ]
        if not acknowledgments:
            acknowledgments.append("No external contributors were detected in this release window.")
        return acknowledgments

    def _format_section_entry(self, pull_request: MergedPullRequest) -> str:
        merged_on = pull_request.merge_date
        return f"{self._clean_title(pull_request.title)} by @{pull_request.author} on {merged_on}."

    def _format_breaking_entry(self, pull_request: MergedPullRequest) -> str:
        return (
            f"{self._clean_title(pull_request.title)} by @{pull_request.author} "
            f"on {pull_request.merge_date}. Review migration guidance before upgrading."
        )

    def _clean_title(self, title: str) -> str:
        return title.rstrip(".")
