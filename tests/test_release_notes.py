from __future__ import annotations

import json
from pathlib import Path

from oss_maintainer_copilot.agents.release_notes import ReleaseNotesGenerator
from oss_maintainer_copilot.schemas.release_notes import ReleaseNotesInput


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def _load_json_fixture(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_generate_release_notes_groups_sections_and_acknowledgments(fixture_root: Path) -> None:
    release_input = ReleaseNotesInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "releases/release_window_mixed.json"))
    )
    result = ReleaseNotesGenerator().generate(release_input)

    assert result.release_title.startswith("v0.3.0 (v0.2.0 -> v0.3.0)")
    assert any("Breaking change:" in item for item in result.highlights)
    assert any("Add contributor guidance generation for issue triage." == item for item in result.highlights)
    assert [section.title for section in result.grouped_markdown_sections] == [
        "Features",
        "Fixes",
        "Documentation",
        "Refactors",
    ]
    assert "rename triage output fields" in result.breaking_changes_section.casefold()
    assert result.contributor_acknowledgments == [
        "@alice contributed 2 merged pull requests.",
        "@bob contributed 1 merged pull request.",
        "@carol contributed 1 merged pull request.",
        "@dave contributed 1 merged pull request.",
    ]


def test_generate_release_notes_handles_no_breaking_changes(fixture_root: Path) -> None:
    release_input = ReleaseNotesInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "releases/release_window_no_breaking.json"))
    )
    result = ReleaseNotesGenerator().generate(release_input)

    assert result.breaking_changes_section == "No breaking changes were identified in this release range."
    assert len(result.grouped_markdown_sections) == 2
    assert result.contributor_acknowledgments == [
        "@alice contributed 1 merged pull request.",
        "@erin contributed 1 merged pull request.",
    ]


def test_render_release_markdown_is_polished_for_github_release(fixture_root: Path) -> None:
    release_input = ReleaseNotesInput.model_validate(
        _load_json_fixture(_fixture(fixture_root, "releases/release_window_mixed.json"))
    )
    generator = ReleaseNotesGenerator()
    result = generator.generate(release_input)
    markdown = generator.render_markdown(result)

    assert markdown.startswith("# ")
    assert "## Highlights" in markdown
    assert "## Features" in markdown
    assert "## Breaking Changes" in markdown
    assert "## Thanks" in markdown
    assert "@alice contributed 2 merged pull requests." in markdown
