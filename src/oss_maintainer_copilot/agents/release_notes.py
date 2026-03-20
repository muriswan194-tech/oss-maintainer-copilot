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
        pull_requests, duplicate_count = self._deduplicate_pull_requests(
            release.merged_pull_requests
        )
        sections = self._group_pull_requests(pull_requests)
        highlights = self._build_highlights(pull_requests)
        grouped_markdown_sections = self._build_markdown_sections(sections)
        breaking_changes_section = self._build_breaking_changes_section(
            pull_requests
        )
        data_quality_notes = self._build_data_quality_notes(
            pull_requests, duplicate_count
        )
        contributor_acknowledgments = self._build_contributor_acknowledgments(
            pull_requests
        )
        release_title = self._build_release_title(release)

        return ReleaseNotesResult(
            release_title=release_title,
            highlights=highlights,
            grouped_markdown_sections=grouped_markdown_sections,
            breaking_changes_section=breaking_changes_section,
            data_quality_notes=data_quality_notes,
            contributor_acknowledgments=contributor_acknowledgments,
        )

    def render_markdown(self, result: ReleaseNotesResult) -> str:
        highlight_lines = (
            "\n".join(f"- {item}" for item in result.highlights)
            or "- No headline changes in this release."
        )
        sections_markdown = "\n\n".join(
            section.markdown for section in result.grouped_markdown_sections
        )
        if not sections_markdown:
            sections_markdown = (
                "## Changes\n"
                "- No categorized pull request groups were generated for this release."
            )
        quality_section = ""
        if result.data_quality_notes:
            quality_lines = "\n".join(
                f"- {item}" for item in result.data_quality_notes
            )
            quality_section = f"\n\n## Data Quality Notes\n{quality_lines}"
        acknowledgments = "\n".join(f"- {line}" for line in result.contributor_acknowledgments)
        return f"""# {result.release_title}

## Highlights
{highlight_lines}

{sections_markdown}{quality_section}

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

    def _deduplicate_pull_requests(
        self,
        pull_requests: list[MergedPullRequest],
    ) -> tuple[list[MergedPullRequest], int]:
        unique_pull_requests: list[MergedPullRequest] = []
        seen_keys: set[tuple[str, str | int]] = set()
        duplicate_count = 0

        for pull_request in pull_requests:
            if pull_request.number is not None:
                key: tuple[str, str | int] = ("number", pull_request.number)
            else:
                key = (
                    "fallback",
                    "|".join(
                        [
                            self._clean_title(pull_request.title).casefold(),
                            pull_request.author.casefold(),
                            pull_request.merge_date,
                        ]
                    ),
                )

            if key in seen_keys:
                duplicate_count += 1
                continue

            seen_keys.add(key)
            unique_pull_requests.append(pull_request)

        return unique_pull_requests, duplicate_count

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
        combined_text = " ".join([pull_request.title, pull_request.body]).casefold()

        if "breaking" in labels or any(
            keyword in combined_text for keyword in BREAKING_KEYWORDS
        ):
            return "breaking"

        for label, group in LABEL_GROUPS.items():
            if label in labels:
                return group

        if "docs" in combined_text or "readme" in combined_text:
            return "docs"
        if "fix" in combined_text or "bug" in combined_text:
            return "fixes"
        if "refactor" in combined_text or "cleanup" in combined_text:
            return "refactors"
        return "features"

    def _build_highlights(self, pull_requests: list[MergedPullRequest]) -> list[str]:
        highlights: list[str] = []
        for pull_request in pull_requests:
            labels = {label.casefold() for label in pull_request.labels}
            title = self._clean_title(pull_request.title)
            if "breaking" in labels or any(
                keyword in " ".join([title, pull_request.body]).casefold()
                for keyword in BREAKING_KEYWORDS
            ):
                highlights.append(
                    f"Breaking change: {self._clean_breaking_title(title)}."
                )
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

    def _build_data_quality_notes(
        self,
        pull_requests: list[MergedPullRequest],
        duplicate_count: int,
    ) -> list[str]:
        notes: list[str] = []
        if not pull_requests:
            notes.append(
                "No merged pull requests were detected for this release window."
            )
            return notes

        unlabeled_count = sum(1 for pull_request in pull_requests if not pull_request.labels)
        missing_body_count = sum(
            1 for pull_request in pull_requests if not pull_request.body.strip()
        )
        missing_number_count = sum(
            1 for pull_request in pull_requests if pull_request.number is None
        )
        missing_upgrade_note_count = sum(
            1
            for pull_request in pull_requests
            if self._categorize_pull_request(pull_request) == "breaking"
            and self._extract_upgrade_note(pull_request) is None
        )

        if duplicate_count:
            notes.append(
                f"Collapsed {duplicate_count} duplicate pull request entr"
                f"{'y' if duplicate_count == 1 else 'ies'} while building this draft."
            )
        if unlabeled_count:
            notes.append(
                f"{unlabeled_count} merged pull request"
                f"{'' if unlabeled_count == 1 else 's'} arrived without labels, so "
                "section grouping relied on title and body heuristics."
            )
        if missing_body_count:
            notes.append(
                f"{missing_body_count} merged pull request"
                f"{'' if missing_body_count == 1 else 's'} did not include body text, "
                "so upgrade note detection may be incomplete."
            )
        if missing_number_count:
            notes.append(
                f"{missing_number_count} merged pull request"
                f"{'' if missing_number_count == 1 else 's'} did not include a PR "
                "number, which limits linking or duplicate detection."
            )
        if missing_upgrade_note_count:
            notes.append(
                f"{missing_upgrade_note_count} breaking change entr"
                f"{'y' if missing_upgrade_note_count == 1 else 'ies'} lacked explicit "
                "migration guidance in the available metadata."
            )

        return notes

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
        upgrade_note = self._extract_upgrade_note(pull_request)
        guidance = (
            f"Upgrade note: {upgrade_note}"
            if upgrade_note is not None
            else "Review migration guidance before upgrading."
        )
        return (
            f"{self._clean_breaking_title(self._clean_title(pull_request.title))} "
            f"by @{pull_request.author} on {pull_request.merge_date}. {guidance}"
        )

    def _clean_title(self, title: str) -> str:
        return title.rstrip(".")

    def _clean_breaking_title(self, title: str) -> str:
        normalized = title.strip()
        for prefix in ("breaking:", "breaking -", "breaking"):
            if normalized.casefold().startswith(prefix):
                normalized = normalized[len(prefix) :].lstrip(" :-")
                break
        return self._clean_title(normalized)

    def _extract_upgrade_note(
        self,
        pull_request: MergedPullRequest,
    ) -> str | None:
        for raw_line in pull_request.body.splitlines():
            line = raw_line.strip().lstrip("-*").strip()
            if not line:
                continue
            if any(keyword in line.casefold() for keyword in BREAKING_KEYWORDS):
                return line.rstrip(".") + "."
        return None
