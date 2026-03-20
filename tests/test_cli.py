from __future__ import annotations

import json
from pathlib import Path

from oss_maintainer_copilot.cli import (
    run_generate_release_notes,
    run_onboarding_map,
    run_repo_intel,
    run_summarize_pr,
    run_triage_issue,
)


def _fixture(path: Path, relative_path: str) -> Path:
    return path / relative_path


def test_cli_triage_issue_writes_json_and_markdown(fixture_root: Path, tmp_path: Path) -> None:
    json_path = tmp_path / "triage.json"
    markdown_path = tmp_path / "triage.md"

    exit_code = run_triage_issue(
        _fixture(fixture_root, "issues/simple_docs_issue.json"),
        json_path,
        markdown_path,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["category"] == "docs"
    assert "recommended_labels" in payload
    assert "<!-- oss-maintainer-copilot:issue-triage -->" in markdown


def test_cli_pr_summary_writes_json_and_markdown(fixture_root: Path, tmp_path: Path) -> None:
    json_path = tmp_path / "pr-summary.json"
    markdown_path = tmp_path / "pr-summary.md"

    exit_code = run_summarize_pr(
        _fixture(fixture_root, "pulls/pr_event_payload.json"),
        json_path,
        markdown_path,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "short_summary" in payload
    assert "changed_areas" in payload
    assert "review_focus" in payload
    assert "risk_assessment" in payload
    assert "<!-- oss-maintainer-copilot:pr-summary -->" in markdown


def test_cli_release_notes_writes_json_and_markdown(fixture_root: Path, tmp_path: Path) -> None:
    json_path = tmp_path / "release-notes.json"
    markdown_path = tmp_path / "release-notes.md"

    exit_code = run_generate_release_notes(
        _fixture(fixture_root, "releases/release_window_mixed.json"),
        json_path,
        markdown_path,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert payload["release_title"].startswith("v0.3.0")
    assert "data_quality_notes" in payload
    assert "grouped_markdown_sections" in payload
    assert markdown.startswith("# ")


def test_cli_repo_intel_writes_json_and_markdown(fixture_root: Path, tmp_path: Path) -> None:
    json_path = tmp_path / "repo-intel.json"
    markdown_path = tmp_path / "repo-intel.md"

    exit_code = run_repo_intel(
        _fixture(fixture_root, "repos/repo_intel_python_toolkit.json"),
        json_path,
        markdown_path,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "repository_summary" in payload
    assert "repository_shape" in payload
    assert "maintainer_workflows" in payload
    assert "<!-- oss-maintainer-copilot:repo-intel -->" in markdown


def test_cli_onboarding_map_writes_json_and_markdown(fixture_root: Path, tmp_path: Path) -> None:
    json_path = tmp_path / "onboarding-map.json"
    markdown_path = tmp_path / "onboarding-map.md"

    exit_code = run_onboarding_map(
        _fixture(fixture_root, "repos/repo_intel_python_toolkit.json"),
        json_path,
        markdown_path,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert exit_code == 0
    assert "first_session_goal" in payload
    assert "reading_order" in payload
    assert "<!-- oss-maintainer-copilot:onboarding-map -->" in markdown
